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
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (response.status === 204) {
    return undefined as T;
  }
  const text = await response.text();
  const data = text ? JSON.parse(text) : {};
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
  demoJob: () => request<Job>("/jobs/demo", { method: "POST" }),
  exportUrl: (id: string) => `${API_BASE}/jobs/${id}/export`,
};
