"""FastAPI backend for AI Scraper."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import PROVIDERS
from src.crawler import crawl
from src.extractor import extract
from src.schema_builder import build_item_model, build_result_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("aiscraping")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AI Scraper API starting")
    yield
    logger.info("AI Scraper API shutting down")


app = FastAPI(title="AI Scraper API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SchemaField(BaseModel):
    name: str
    type: str
    description: str = ""


class ScrapeRequest(BaseModel):
    url: str
    fields: list[SchemaField]
    provider: str = "OpenAI"
    model: str = "gpt-4.1-mini"  # display name
    api_key: str


class ScrapeResponse(BaseModel):
    items: list[dict]
    markdown_length: int
    provider: str
    model: str


def _resolve_litellm_model(provider: str, display_name: str) -> str:
    """Convert a display model name to a LiteLLM provider string."""
    provider_info = PROVIDERS.get(provider)
    if not provider_info:
        raise ValueError(f"Unknown provider: {provider}")
    for name, litellm_id in provider_info["models"]:
        if name == display_name:
            return litellm_id
    raise ValueError(f"Unknown model: {display_name}")


@app.get("/api/providers")
def get_providers():
    """Return available providers and their model display names."""
    return {
        name: {
            "models": [m[0] for m in info["models"]],
            "env_key": info["env_key"],
        }
        for name, info in PROVIDERS.items()
    }


@app.post("/api/scrape", response_model=ScrapeResponse)
def scrape(req: ScrapeRequest):
    """Crawl a URL and extract structured data."""
    if not req.fields:
        raise HTTPException(400, "At least one schema field is required")
    if not req.url:
        raise HTTPException(400, "URL is required")

    try:
        litellm_model = _resolve_litellm_model(req.provider, req.model)
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Crawl
    logger.info("Crawling %s", req.url)
    crawl_result = crawl(req.url)
    if not crawl_result.success:
        raise HTTPException(502, f"Crawl failed: {crawl_result.error}")

    # Build schema
    schema_dict = {
        f.name: {"type": f.type, "description": f.description}
        for f in req.fields
    }
    item_model = build_item_model("ScrapeItem", schema_dict)
    result_model = build_result_model(item_model)

    # Extract via LiteLLM
    try:
        result = extract(
            markdown=crawl_result.markdown,
            result_model=result_model,
            litellm_model=litellm_model,
            api_key=req.api_key,
        )
    except Exception as e:
        logger.exception("Extraction failed")
        raise HTTPException(500, f"Extraction failed: {e}")

    items = [item.model_dump() for item in result.items]
    return ScrapeResponse(
        items=items,
        markdown_length=len(crawl_result.markdown),
        provider=req.provider,
        model=req.model,
    )
