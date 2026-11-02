import type { Job, JobDetail, LlmConfig, User } from "./types";

const API_BASE = "/api";
const TOKEN_KEY = "vulnlab.token";
const LLM_KEY = "vulnlab.llm";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export function loadLlmConfig(): LlmConfig {
  try {
    const raw = localStorage.getItem(LLM_KEY);
    if (raw) return JSON.parse(raw) as LlmConfig;
  } catch {
    /* ignore corrupted config */
  }
  return { provider: "deepseek", baseUrl: "https://api.deepseek.com/v1", model: "deepseek-chat", apiKey: "" };
}

export function saveLlmConfig(config: LlmConfig) {
  localStorage.setItem(LLM_KEY, JSON.stringify(config));
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new ApiError("无法连接到服务，请确认 Docker 服务已启动或检查网关地址", 0);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  const text = await response.text();
  let data: unknown = {};
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text.slice(0, 300) };
    }
  }
  if (!response.ok) {
    const detail = (data as { detail?: unknown }).detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((item) => (item as { msg?: string }).msg ?? "").join("；")
          : `请求失败（${response.status}）`;
    throw new ApiError(message || `请求失败（${response.status}）`, response.status);
  }
  return data as T;
}

async function downloadReport(id: string): Promise<void> {
  const headers = new Headers();
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/jobs/${encodeURIComponent(id)}/export`, { headers });
  } catch {
    throw new ApiError("无法连接到服务，请确认 Docker 服务已启动或检查网关地址", 0);
  }
  if (!response.ok) {
    const text = await response.text();
    let detail = text.slice(0, 300);
    try {
      const data = JSON.parse(text) as { detail?: unknown };
      if (typeof data.detail === "string") detail = data.detail;
    } catch {
      /* 网关错误页可能是 HTML，保留原始短消息 */
    }
    throw new ApiError(detail || `导出失败（${response.status}）`, response.status);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `vuln-report-${id.slice(0, 8)}.md`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export const api = {
  register: (email: string, password: string, displayName: string) =>
    request<{ access_token: string; user: User }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name: displayName }),
    }),
  login: (email: string, password: string) =>
    request<{ access_token: string; user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<User>("/auth/me"),
  jobs: (limit = 20) => request<{ items: Job[]; total: number }>(`/jobs?limit=${limit}`),
  job: (id: string) => request<JobDetail>(`/jobs/${id}`),
  deleteJob: (id: string) => request<void>(`/jobs/${id}`, { method: "DELETE" }),
  createJob: (file: File, config: LlmConfig | null) => {
    const form = new FormData();
    form.append("file", file);
    if (config?.apiKey) {
      form.append("api_key", config.apiKey);
      form.append("provider", config.provider);
      form.append("base_url", config.baseUrl);
      form.append("model", config.model);
    }
    return request<Job>("/jobs", { method: "POST", body: form });
  },
  demoJob: (config: LlmConfig | null = null) => {
    const form = new FormData();
    if (config?.apiKey) {
      form.append("api_key", config.apiKey);
      form.append("provider", config.provider);
      form.append("base_url", config.baseUrl);
      form.append("model", config.model);
    }
    return request<Job>("/jobs/demo", { method: "POST", body: form });
  },
  exportJob: downloadReport,
};
