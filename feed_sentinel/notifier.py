"""Webhook notification dispatcher for trend alerts and digest summaries."""

from __future__ import annotations
import httpx
from typing import Any
from .models import PipelineResult


class WebhookNotifier:
    """Dispatches pipeline digests and breaking trend alerts to external webhook endpoints."""

    def __init__(self, webhook_url: str, timeout: float = 10.0):
        self.webhook_url = webhook_url
        self.timeout = timeout

    def build_payload(self, result: PipelineResult) -> dict[str, Any]:
        """Format an alert payload compatible with Slack, Discord, and standard webhooks."""
        trends_str = ", ".join(f"{t.keyword} ({t.frequency}x)" for t in result.top_trends[:5])
        content_text = (
            f"📡 **Feed Sentinel Intelligence Digest**\n"
            f"• **Articles Processed:** {result.articles_fetched} fetched, {result.new_articles_stored} new\n"
            f"• **Top Detected Trends:** {trends_str or 'None'}\n"
            f"• **Active Sources:** {result.total_sources}"
        )

        return {
            "text": content_text,
            "content": content_text,  # For Discord
            "pipeline_summary": {
                "timestamp": result.timestamp.isoformat(),
                "articles_fetched": result.articles_fetched,
                "new_articles_stored": result.new_articles_stored,
                "top_trends": [
                    {"keyword": t.keyword, "frequency": t.frequency, "sentiment": t.sentiment_avg}
                    for t in result.top_trends[:5]
                ],
            },
        }

    async def send_async(self, result: PipelineResult) -> bool:
        """Send notification asynchronously."""
        payload = self.build_payload(result)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(self.webhook_url, json=payload)
            return resp.is_success

    def send_sync(self, result: PipelineResult) -> bool:
        """Send notification synchronously."""
        payload = self.build_payload(result)
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(self.webhook_url, json=payload)
            return resp.is_success
