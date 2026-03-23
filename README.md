# AI Scraper

> **v2.0** — Production-grade rebuild of the original [LLM web scraping PoC](https://medium.com/@ignacio.cplatas/enhancing-web-scraping-with-large-language-models-a-modern-approach-6216d5bba8d5) (2024).

Define a schema, provide a URL, get structured data. No CSS selectors, no XPath, no manual HTML parsing.

## What changed (2024 → 2026)

| Layer | v1 (2024) | v2 (2026) |
|-------|-----------|-----------|
| Crawling | `requests` + BeautifulSoup | **Crawl4AI** — async Playwright, JS rendering, clean markdown |
| Extraction | LangChain + PydanticOutputParser | **Native structured output** — `openai.parse()` / `anthropic.parse()` |
| Schema | 3 types (str, int, float) | 5 types + dynamic Pydantic v2 models |
| Models | OpenAI only | **OpenAI + Anthropic** |
| Error handling | None | Retries, exponential backoff, user-facing messages |
| UI | Custom Streamlit rows | `st.data_editor` + `st.status` |

The original was a PoC — no error handling, no retries, one model, fragile parsing. This rebuild produces a production-grade tool with the same time investment.

## Quick Start

```bash
# Clone and install
git clone https://github.com/NachoCP/AIScraping.git
cd AIScraping
pip install .

# Install browser (needed for Crawl4AI)
crawl4ai-setup

# Set your API key
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and/or ANTHROPIC_API_KEY

# Run
streamlit run app.py
```

## Docker

```bash
docker build -t aiscraper .
docker run -p 8501:8501 --env-file .env aiscraper
```

## How it works

1. **Define your schema** — Use the interactive table to add fields (name, type, description)
2. **Enter a URL** — Any webpage, including JS-rendered pages
3. **Extract** — Crawl4AI fetches and converts the page to markdown, then the LLM extracts structured data matching your schema
4. **Download** — Get your data as JSON

## Architecture

```
Streamlit UI → Crawl4AI (async, Playwright) → LLM SDK (structured output) → JSON
```

- `src/crawler.py` — Crawl4AI wrapper with ThreadPoolExecutor bridge for Streamlit
- `src/extractor.py` — Multi-model extraction (OpenAI / Anthropic) with tenacity retry
- `src/schema_builder.py` — Dynamic Pydantic v2 model creation
- `src/config.py` — Provider configuration and settings

## Requirements

- Python 3.11+
- An OpenAI or Anthropic API key

## Original Article

This project accompanies the article: [Enhancing Web Scraping with Large Language Models: A Modern Approach](https://medium.com/@ignacio.cplatas/enhancing-web-scraping-with-large-language-models-a-modern-approach-6216d5bba8d5)
