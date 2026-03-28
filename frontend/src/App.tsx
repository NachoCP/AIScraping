import { useEffect, useState, useCallback } from "react";
import {
  Globe,
  Plus,
  Trash2,
  Download,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Search,
  Zap,
  Table,
  Settings,
} from "lucide-react";
import { fetchProviders, scrape } from "./api";
import type {
  SchemaField,
  Providers,
  ScrapeResponse,
  ExtractionStatus,
} from "./types";

const FIELD_TYPES = ["string", "integer", "float", "boolean", "list[string]"];

function newField(): SchemaField {
  return { id: crypto.randomUUID(), name: "", type: "string", description: "" };
}

export default function App() {
  const [providers, setProviders] = useState<Providers>({});
  const [provider, setProvider] = useState("OpenAI");
  const [model, setModel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [url, setUrl] = useState("");
  const [fields, setFields] = useState<SchemaField[]>([newField()]);
  const [status, setStatus] = useState<ExtractionStatus>("idle");
  const [statusMsg, setStatusMsg] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<ScrapeResponse | null>(null);

  useEffect(() => {
    fetchProviders().then((p) => {
      setProviders(p);
      const first = Object.keys(p)[0];
      if (first) {
        setProvider(first);
        setModel(p[first].models[0]);
      }
    });
  }, []);

  useEffect(() => {
    if (providers[provider]) {
      setModel(providers[provider].models[0]);
    }
  }, [provider, providers]);

  const updateField = useCallback(
    (id: string, key: keyof SchemaField, value: string) => {
      setFields((prev) =>
        prev.map((f) => (f.id === id ? { ...f, [key]: value } : f))
      );
    },
    []
  );

  const removeField = useCallback((id: string) => {
    setFields((prev) => (prev.length > 1 ? prev.filter((f) => f.id !== id) : prev));
  }, []);

  const handleExtract = async () => {
    setError("");
    setResult(null);

    const validFields = fields.filter((f) => f.name.trim());
    if (!validFields.length) return setError("Add at least one field to the schema.");
    if (!url.trim()) return setError("Enter a URL to scrape.");
    if (!apiKey.trim()) return setError("Enter your API key.");

    try {
      setStatus("crawling");
      setStatusMsg("Crawling page...");

      const res = await scrape({
        url: url.trim(),
        fields: validFields.map(({ name, type, description }) => ({
          name: name.trim(),
          type,
          description,
        })),
        provider,
        model,
        api_key: apiKey,
      });

      setStatus("done");
      setStatusMsg(`Extracted ${res.items.length} items`);
      setResult(res);
    } catch (e) {
      setStatus("error");
      setError(e instanceof Error ? e.message : "Unknown error");
      setStatusMsg("");
    }
  };

  const downloadJSON = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result.items, null, 2)], {
      type: "application/json",
    });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "extracted_data.json";
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const columns = result?.items.length
    ? Object.keys(result.items[0])
    : [];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      {/* Header */}
      <header className="border-b border-zinc-800/60">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center">
              <Globe className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">AI Scraper</h1>
              <p className="text-xs text-zinc-500">v2 — Crawl4AI + Structured Output</p>
            </div>
          </div>

          {/* Settings inline */}
          <div className="flex items-center gap-3">
            <Settings className="w-4 h-4 text-zinc-500" />
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-violet-500"
            >
              {Object.keys(providers).map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-violet-500"
            >
              {(providers[provider]?.models ?? []).map((m) => (
                <option key={m}>{m}</option>
              ))}
            </select>
            <input
              type="password"
              placeholder="API Key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-sm w-40 focus:outline-none focus:ring-1 focus:ring-violet-500 placeholder:text-zinc-600"
            />
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        {/* Schema Builder */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Table className="w-4 h-4 text-violet-400" />
            <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">
              Schema
            </h2>
          </div>

          <div className="bg-zinc-900/50 border border-zinc-800/60 rounded-xl overflow-hidden">
            {/* Table header */}
            <div className="grid grid-cols-[1fr_140px_1fr_40px] gap-0 bg-zinc-900 border-b border-zinc-800/60 px-4 py-2.5">
              <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
                Field Name
              </span>
              <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
                Type
              </span>
              <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
                Description
              </span>
              <span />
            </div>

            {/* Rows */}
            {fields.map((field) => (
              <div
                key={field.id}
                className="grid grid-cols-[1fr_140px_1fr_40px] gap-0 border-b border-zinc-800/30 last:border-b-0 group"
              >
                <input
                  value={field.name}
                  onChange={(e) => updateField(field.id, "name", e.target.value)}
                  placeholder="e.g. title"
                  className="bg-transparent px-4 py-3 text-sm focus:outline-none focus:bg-zinc-800/30 placeholder:text-zinc-700"
                />
                <select
                  value={field.type}
                  onChange={(e) => updateField(field.id, "type", e.target.value)}
                  className="bg-transparent px-2 py-3 text-sm focus:outline-none focus:bg-zinc-800/30 border-x border-zinc-800/30"
                >
                  {FIELD_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
                <input
                  value={field.description}
                  onChange={(e) =>
                    updateField(field.id, "description", e.target.value)
                  }
                  placeholder="What this field represents"
                  className="bg-transparent px-4 py-3 text-sm focus:outline-none focus:bg-zinc-800/30 placeholder:text-zinc-700"
                />
                <button
                  onClick={() => removeField(field.id)}
                  className="flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-zinc-600 hover:text-red-400"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}

            {/* Add row */}
            <button
              onClick={() => setFields((prev) => [...prev, newField()])}
              className="w-full flex items-center justify-center gap-2 py-2.5 text-sm text-zinc-500 hover:text-violet-400 hover:bg-zinc-800/30 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              Add field
            </button>
          </div>
        </section>

        {/* URL + Extract */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Search className="w-4 h-4 text-violet-400" />
            <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">
              Extract
            </h2>
          </div>

          <div className="flex gap-3">
            <input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/products"
              className="flex-1 bg-zinc-900/50 border border-zinc-800/60 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-violet-500 placeholder:text-zinc-600"
            />
            <button
              onClick={handleExtract}
              disabled={status === "crawling" || status === "extracting"}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl text-sm font-medium transition-all"
            >
              {status === "crawling" || status === "extracting" ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Zap className="w-4 h-4" />
              )}
              Extract
            </button>
          </div>

          {/* Status */}
          {statusMsg && (
            <div
              className={`mt-3 flex items-center gap-2 text-sm ${
                status === "done"
                  ? "text-emerald-400"
                  : status === "error"
                  ? "text-red-400"
                  : "text-zinc-400"
              }`}
            >
              {status === "done" && <CheckCircle2 className="w-4 h-4" />}
              {status === "error" && <AlertCircle className="w-4 h-4" />}
              {(status === "crawling" || status === "extracting") && (
                <Loader2 className="w-4 h-4 animate-spin" />
              )}
              {statusMsg}
            </div>
          )}

          {error && !statusMsg && (
            <div className="mt-3 flex items-center gap-2 text-sm text-red-400">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}
        </section>

        {/* Results */}
        {result && result.items.length > 0 && (
          <section>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Table className="w-4 h-4 text-emerald-400" />
                <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">
                  Results
                </h2>
                <span className="ml-2 text-xs text-zinc-600">
                  {result.items.length} items &middot; {result.provider}/{result.model}
                </span>
              </div>
              <button
                onClick={downloadJSON}
                className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                Download JSON
              </button>
            </div>

            <div className="bg-zinc-900/50 border border-zinc-800/60 rounded-xl overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-zinc-800/60">
                    {columns.map((col) => (
                      <th
                        key={col}
                        className="text-left px-4 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider bg-zinc-900"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.items.map((item, i) => (
                    <tr
                      key={i}
                      className="border-b border-zinc-800/30 last:border-b-0 hover:bg-zinc-800/20"
                    >
                      {columns.map((col) => (
                        <td key={col} className="px-4 py-3 text-zinc-300">
                          {Array.isArray(item[col])
                            ? (item[col] as string[]).join(", ")
                            : String(item[col] ?? "")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-800/60 mt-auto">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between text-xs text-zinc-600">
          <span>AI Scraper v2.0 — From PoC to Production</span>
          <a
            href="https://github.com/NachoCP/AIScraping"
            target="_blank"
            rel="noopener"
            className="hover:text-zinc-400 transition-colors"
          >
            GitHub
          </a>
        </div>
      </footer>
    </div>
  );
}
