export interface SchemaField {
  id: string;
  name: string;
  type: string;
  description: string;
}

export interface ScrapeRequest {
  url: string;
  fields: { name: string; type: string; description: string }[];
  provider: string;
  model: string;
  api_key: string;
}

export interface ScrapeResponse {
  items: Record<string, unknown>[];
  markdown_length: number;
  provider: string;
  model: string;
}

export interface ProviderInfo {
  models: string[];
  env_key: string;
}

export type Providers = Record<string, ProviderInfo>;

export type ExtractionStatus = "idle" | "crawling" | "extracting" | "done" | "error";
