export type Severity = "critical" | "high" | "medium" | "low" | "info";
export type Verdict = "vulnerable" | "safe" | "uncertain";

export interface User {
  id: string;
  email: string;
  display_name: string;
  created_at: string;
}

export interface Finding {
  id: string;
  category: string;
  severity: Severity;
  verdict: Verdict;
  title: string;
  file_path: string;
  line: number;
  snippet: string;
  explanation: string;
  remediation: string;
  confidence: number;
  source: "static" | "llm" | "dataflow";
  flow?: { line: number; code: string; note: string }[];
}

export interface Job {
  id: string;
  filename: string;
  size_bytes: number;
  file_count: number;
  status: "queued" | "running" | "succeeded" | "failed";
  stage: string;
  progress: number;
  error: string;
  provider: string;
  model: string;
  llm_enabled: boolean;
  llm_candidate_count: number;
  llm_call_count: number;
  findings_count: number;
  severity_counts: Partial<Record<Severity, number>>;
  languages: Record<string, number>;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface JobDetail extends Job {
  findings: Finding[];
}

export interface LlmConfig {
  provider: string;
  baseUrl: string;
  model: string;
  apiKey: string;
}

export const PROVIDERS: { id: string; label: string; baseUrl: string; models: string[] }[] = [
  { id: "openai", label: "OpenAI", baseUrl: "https://api.openai.com/v1", models: ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"] },
  { id: "deepseek", label: "DeepSeek", baseUrl: "https://api.deepseek.com/v1", models: ["deepseek-chat", "deepseek-reasoner"] },
  { id: "moonshot", label: "Moonshot", baseUrl: "https://api.moonshot.cn/v1", models: ["moonshot-v1-32k", "kimi-latest"] },
  { id: "qwen", label: "通义千问", baseUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1", models: ["qwen-plus", "qwen-max"] },
  { id: "custom", label: "自定义（OpenAI 兼容）", baseUrl: "", models: ["gpt-4o-mini"] },
];
