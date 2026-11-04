"""Data models for Feed Sentinel."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class FeedSource:
    id: str
    name: str
    url: str
    category: str = "general"
    enabled: bool = True


@dataclass
class Article:
    id: str
    source_name: str
    title: str
    url: str
    published_at: datetime
    summary: str
    content: str
    author: Optional[str] = None
    category: str = "general"
    keywords: List[str] = field(default_factory=list)
    sentiment_score: float = 0.0  # -1.0 to 1.0


@dataclass
class TrendMetric:
    keyword: str
    frequency: int
    sentiment_avg: float
    sample_headlines: List[str]


@dataclass
class PipelineResult:
    timestamp: datetime
    total_sources: int
    articles_fetched: int
    new_articles_stored: int
    top_trends: List[TrendMetric]
    articles: List[Article]
