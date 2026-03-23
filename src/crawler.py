"""Crawl4AI wrapper — async crawl bridged to sync for Streamlit."""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

logger = logging.getLogger("aiscraping")


@dataclass
class CrawlResult:
    success: bool
    markdown: str
    error: str | None = None


def _run_async(coro):
    """Run an async coroutine from sync Streamlit context using a dedicated thread."""
    with ThreadPoolExecutor(1) as pool:
        return pool.submit(lambda: asyncio.run(coro)).result()


async def _crawl_async(url: str) -> CrawlResult:
    """Crawl a URL and return clean markdown."""
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        page_timeout=30000,
    )

    async with AsyncWebCrawler(config=browser_config, thread_safe=True) as crawler:
        result = await crawler.arun(url=url, config=run_config)

    if not result.success:
        return CrawlResult(success=False, markdown="", error=result.error_message)

    return CrawlResult(success=True, markdown=result.markdown.raw_markdown)


def crawl(url: str) -> CrawlResult:
    """Sync entry point — crawls a URL and returns markdown content."""
    logger.info("Crawling %s", url)
    try:
        return _run_async(_crawl_async(url))
    except Exception as e:
        logger.exception("Crawl failed for %s", url)
        return CrawlResult(success=False, markdown="", error=str(e))
