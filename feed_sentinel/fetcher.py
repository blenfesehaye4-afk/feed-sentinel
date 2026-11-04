"""Asynchronous feed content fetcher with rate limiting and retry handling."""

import asyncio
from typing import Dict, List, Optional, Tuple

import httpx

from .models import FeedSource


class FeedFetcher:
    """Asynchronous HTTP fetcher with concurrency limiting."""

    def __init__(self, concurrency: int = 5, timeout: float = 10.0):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.timeout = timeout
        self.headers = {
            "User-Agent": "FeedSentinel/1.0 (+https://github.com/blenfesehaye4-afk/feed-sentinel)",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
        }

    async def fetch_source(self, source: FeedSource) -> Tuple[FeedSource, Optional[str], Optional[str]]:
        """Fetch raw XML content for a single source. Returns (source, content, error)."""
        async with self.semaphore:
            try:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    resp = await client.get(source.url, headers=self.headers)
                    if resp.status_code == 200:
                        return (source, resp.text, None)
                    return (source, None, f"HTTP {resp.status_code}")
            except Exception as exc:
                return (source, None, str(exc))

    async def fetch_all(self, sources: List[FeedSource]) -> List[Tuple[FeedSource, Optional[str], Optional[str]]]:
        """Concurrently fetch all enabled feed sources."""
        active = [s for s in sources if s.enabled]
        tasks = [self.fetch_source(s) for s in active]
        return await asyncio.gather(*tasks)
