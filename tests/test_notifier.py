import pytest
from datetime import datetime, timezone
from feed_sentinel.models import PipelineResult, TrendMetric
from feed_sentinel.notifier import WebhookNotifier


def test_webhook_notifier_payload_format():
    result = PipelineResult(
        timestamp=datetime.now(timezone.utc),
        total_sources=2,
        articles_fetched=10,
        new_articles_stored=5,
        top_trends=[
            TrendMetric(keyword="ai", frequency=8, sentiment_avg=0.5, sample_headlines=["AI launch"]),
        ],
        articles=[],
    )

    notifier = WebhookNotifier(webhook_url="https://hooks.example.com/services/123")
    payload = notifier.build_payload(result)

    assert "text" in payload
    assert "content" in payload
    assert "Feed Sentinel Intelligence Digest" in payload["text"]
    assert "ai (8x)" in payload["text"]
    assert payload["pipeline_summary"]["articles_fetched"] == 10
