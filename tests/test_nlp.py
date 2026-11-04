"""Unit tests for NLP and trend analysis."""

from datetime import datetime, timezone
from feed_sentinel.models import Article
from feed_sentinel.nlp import TrendAnalyzer


def test_sentiment_scoring():
    pos_text = "Innovative breakthrough release brings powerful improvement and success!"
    neg_text = "Critical security vulnerability and severe bug exploit causes outage failure."

    pos_score = TrendAnalyzer.compute_sentiment(pos_text)
    neg_score = TrendAnalyzer.compute_sentiment(neg_text)

    assert pos_score > 0
    assert neg_score < 0


def test_article_enrichment_and_trends():
    now = datetime.now(timezone.utc)
    articles = [
        Article(
            id="1",
            source_name="Src1",
            title="FastAPI Web Framework Updates",
            url="https://a.com/1",
            published_at=now,
            summary="FastAPI introduces asynchronous performance breakthrough.",
            content="FastAPI introduces asynchronous performance breakthrough.",
        ),
        Article(
            id="2",
            source_name="Src2",
            title="FastAPI in Production",
            url="https://a.com/2",
            published_at=now,
            summary="Deploying modern FastAPI services in Kubernetes clusters.",
            content="Deploying modern FastAPI services in Kubernetes clusters.",
        ),
    ]

    TrendAnalyzer.enrich_articles(articles)
    assert "fastapi" in articles[0].keywords
    assert articles[0].sentiment_score >= 0

    trends = TrendAnalyzer.extract_top_trends(articles, top_n=3)
    assert len(trends) > 0
    # 'fastapi' appears in both articles
    keywords = [t.keyword for t in trends]
    assert "fastapi" in keywords
