"""Unit tests for pipeline storage and reporting."""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

from feed_sentinel.models import Article, PipelineResult, TrendMetric
from feed_sentinel.generator import ReportGenerator
from feed_sentinel.storage import ArticleStorage


def test_article_storage_deduplication():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test.db"
        storage = ArticleStorage(db_path=str(db_path))

        now = datetime.now(timezone.utc)
        art1 = Article(id="a1", source_name="Test", title="T1", url="https://x.com/1", published_at=now, summary="S1", content="S1")
        art2 = Article(id="a2", source_name="Test", title="T2", url="https://x.com/2", published_at=now, summary="S2", content="S2")

        # First insert
        inserted1 = storage.store_articles([art1, art2])
        assert inserted1 == 2
        assert storage.total_count() == 2

        # Duplicate insert
        inserted2 = storage.store_articles([art1])
        assert inserted2 == 0  # Deduplicated!
        assert storage.total_count() == 2


def test_report_generation_markdown_and_html():
    now = datetime.now(timezone.utc)
    res = PipelineResult(
        timestamp=now,
        total_sources=2,
        articles_fetched=1,
        new_articles_stored=1,
        top_trends=[
            TrendMetric(keyword="python", frequency=5, sentiment_avg=0.5, sample_headlines=["Python 3.13 Launched"])
        ],
        articles=[
            Article(id="a1", source_name="Test Blog", title="Python 3.13 Launched", url="https://py.org", published_at=now, summary="Great update", content="Great update")
        ],
    )
    generator = ReportGenerator()
    md = generator.to_markdown(res)
    html = generator.to_html(res)

    assert "# 📡 Feed Sentinel Intelligence Digest" in md
    assert "#python" in md
    assert "<!DOCTYPE html>" in html
    assert "Feed Sentinel Daily Brief" in html
