import type { Providers, ScrapeRequest, ScrapeResponse } from "./types";

const BASE = "/api";

export async function fetchProviders(): Promise<Providers> {
  const res = await fetch(`${BASE}/providers`);
  if (!res.ok) throw new Error("Failed to fetch providers");
  return res.json();
}

export async function scrape(req: ScrapeRequest): Promise<ScrapeResponse> {
  const res = await fetch(`${BASE}/scrape`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || "Extraction failed");
  }
  return res.json();
}
