"""Report generators for Markdown, HTML newsletters, and Rich terminal output."""

import html
from datetime import datetime
from typing import List

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import PipelineResult


class ReportGenerator:
    """Renders pipeline results to terminal, Markdown, and HTML."""

    def __init__(self, console: Console = None):
        self.console = console or Console()

    def print_terminal(self, res: PipelineResult) -> None:
        """Render stylish terminal dashboard."""
        header_text = Text()
        header_text.append("📡 FEED SENTINEL INTELLIGENCE DIGEST\n", style="bold cyan")
        header_text.append(f"Processed: {res.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}  |  ", style="dim")
        header_text.append(f"Sources: {res.total_sources}  |  ", style="bold green")
        header_text.append(f"Fetched: {res.articles_fetched} articles  |  ", style="bold yellow")
        header_text.append(f"New Stored: {res.new_articles_stored}", style="bold magenta")
        self.console.print(Panel(header_text, box=ROUNDED, border_style="cyan"))

        # Trending Topics Table
        if res.top_trends:
            trend_table = Table(title="📈 Emerging Topics & Sentiment", box=ROUNDED, header_style="bold magenta")
            trend_table.add_column("Keyword", style="bold white")
            trend_table.add_column("Mentions", justify="right", style="cyan")
            trend_table.add_column("Sentiment", justify="center")
            trend_table.add_column("Sample Headline", style="dim")

            for t in res.top_trends[:6]:
                sent_style = "green" if t.sentiment_avg > 0.1 else ("red" if t.sentiment_avg < -0.1 else "white")
                sent_label = f"[{sent_style}]{t.sentiment_avg:+.2f}[/{sent_style}]"
                sample = t.sample_headlines[0][:50] + "..." if t.sample_headlines else ""
                trend_table.add_row(f"#{t.keyword}", str(t.frequency), sent_label, sample)
            self.console.print(trend_table)

        # Articles Table
        art_table = Table(title="📰 Recent Monitored Feed Items", box=ROUNDED, header_style="bold green")
        art_table.add_column("Source", style="bold cyan", width=18)
        art_table.add_column("Title", style="bold white")
        art_table.add_column("Category", style="yellow", width=14)
        art_table.add_column("Published", style="dim", width=14)

        for art in res.articles[:10]:
            date_str = art.published_at.strftime("%b %d, %H:%M")
            art_table.add_row(art.source_name, art.title[:65] + ("..." if len(art.title) > 65 else ""), art.category, date_str)
        self.console.print(art_table)

    def to_markdown(self, res: PipelineResult) -> str:
        """Export as GitHub-flavored Markdown."""
        md = []
        md.append("# 📡 Feed Sentinel Intelligence Digest\n")
        md.append(f"- **Generated:** `{res.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}`")
        md.append(f"- **Sources Tracked:** `{res.total_sources}`")
        md.append(f"- **Articles Ingested:** `{res.articles_fetched}`")
        md.append(f"- **New Additions:** `{res.new_articles_stored}`\n")

        if res.top_trends:
            md.append("## 📈 Emerging Topics & Sentiment\n")
            md.append("| Trend Keyword | Mentions | Sentiment Index | Sample Headline |")
            md.append("|:---|---:|:---:|:---|")
            for t in res.top_trends:
                sample = html.escape(t.sample_headlines[0]) if t.sample_headlines else "-"
                sentiment_icon = "🟢" if t.sentiment_avg > 0.1 else ("🔴" if t.sentiment_avg < -0.1 else "⚪")
                md.append(f"| `#{t.keyword}` | {t.frequency} | {sentiment_icon} {t.sentiment_avg:+.2f} | {sample} |")

        md.append("\n## 📰 Monitored Articles\n")
        for art in res.articles:
            date_str = art.published_at.strftime("%Y-%m-%d %H:%M")
            md.append(f"### [{art.title}]({art.url})")
            md.append(f"*{art.source_name}* • `{art.category}` • *{date_str}*\n")
            md.append(f"> {art.summary}\n")

        return "\n".join(md)

    def to_html(self, res: PipelineResult) -> str:
        """Export as clean standalone newsletter HTML."""
        items_html = ""
        for art in res.articles[:20]:
            items_html += f"""
            <div style="padding: 16px; border-bottom: 1px solid #e1e4e8; margin-bottom: 12px;">
                <h3 style="margin: 0 0 6px 0;"><a href="{art.url}" style="color: #0366d6; text-decoration: none;">{html.escape(art.title)}</a></h3>
                <div style="font-size: 13px; color: #586069; margin-bottom: 8px;">
                    <strong>{html.escape(art.source_name)}</strong> • {art.category} • {art.published_at.strftime('%b %d, %Y')}
                </div>
                <p style="margin: 0; color: #24292e; font-size: 14px; line-height: 1.5;">{html.escape(art.summary)}</p>
            </div>
            """

        trends_html = ""
        for t in res.top_trends[:8]:
            trends_html += f"""
            <span style="display: inline-block; background: #eef2ff; color: #3730a3; padding: 4px 10px; border-radius: 12px; margin: 4px; font-size: 13px; font-weight: 500;">
                #{html.escape(t.keyword)} ({t.frequency})
            </span>
            """

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Feed Sentinel Intelligence Digest</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f6f8fa; padding: 24px; color: #24292e;">
    <div style="max-width: 800px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #d1d5db; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="background: #0f172a; color: #ffffff; padding: 24px;">
            <h1 style="margin: 0 0 8px 0; font-size: 24px;">📡 Feed Sentinel Daily Brief</h1>
            <p style="margin: 0; color: #94a3b8; font-size: 14px;">Ingested {res.articles_fetched} articles across {res.total_sources} verified sources.</p>
        </div>
        <div style="padding: 24px; border-bottom: 1px solid #e1e4e8; background: #fafbfc;">
            <h4 style="margin: 0 0 8px 0; text-transform: uppercase; font-size: 12px; color: #6b7280; letter-spacing: 0.05em;">Key Emerging Trends</h4>
            {trends_html}
        </div>
        <div style="padding: 24px;">
            <h4 style="margin: 0 0 16px 0; text-transform: uppercase; font-size: 12px; color: #6b7280; letter-spacing: 0.05em;">Latest Ingested Articles</h4>
            {items_html}
        </div>
    </div>
</body>
</html>
"""
