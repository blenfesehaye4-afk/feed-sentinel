"""CLI commands for Feed Sentinel."""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from .fetcher import FeedFetcher
from .generator import ReportGenerator
from .models import FeedSource, PipelineResult
from .nlp import TrendAnalyzer
from .parser import FeedParser
from .storage import ArticleStorage


def load_sources(config_path: Path) -> List[FeedSource]:
    """Load feed sources from JSON configuration."""
    if not config_path.exists():
        # Fallback default sources
        return [
            FeedSource(id="github", name="GitHub Blog", url="https://github.blog/engineering/feed/", category="engineering"),
            FeedSource(id="python", name="Python Insider", url="https://pythoninsider.blogspot.com/feeds/posts/default", category="python"),
        ]

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [FeedSource(**item) for item in data]


async def run_pipeline(
    config_path: Path,
    db_path: Path,
    output_dir: Path,
    formats: List[str],
) -> PipelineResult:
    """Execute ingestion, NLP analysis, storage, and report generation."""
    sources = load_sources(config_path)
    fetcher = FeedFetcher()
    storage = ArticleStorage(db_path=str(db_path))

    # 1. Fetch
    raw_results = await fetcher.fetch_all(sources)

    # 2. Parse
    all_articles = []
    for source, content, error in raw_results:
        if content:
            arts = FeedParser.parse(source, content)
            all_articles.extend(arts)

    # 3. NLP Enrichment
    TrendAnalyzer.enrich_articles(all_articles)
    top_trends = TrendAnalyzer.extract_top_trends(all_articles)

    # 4. Storage & Deduplication
    new_stored = storage.store_articles(all_articles)

    # 5. Assemble Pipeline Result
    result = PipelineResult(
        timestamp=datetime.now(timezone.utc),
        total_sources=len(sources),
        articles_fetched=len(all_articles),
        new_articles_stored=new_stored,
        top_trends=top_trends,
        articles=all_articles,
    )

    # 6. Generate Outputs
    reporter = ReportGenerator()
    output_dir.mkdir(parents=True, exist_ok=True)
    date_str = result.timestamp.strftime("%Y%m%d_%H%M%S")

    if "terminal" in formats:
        reporter.print_terminal(result)

    if "md" in formats or "markdown" in formats:
        md_file = output_dir / f"digest_{date_str}.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(reporter.to_markdown(result))
        print(f"Markdown report generated: {md_file}")

    if "html" in formats:
        html_file = output_dir / f"digest_{date_str}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(reporter.to_html(result))
        print(f"HTML digest generated: {html_file}")

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="feed-sentinel",
        description="📡 Feed Sentinel: Intelligent RSS/Atom Content Ingestion & Trend Pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Command: run
    run_cmd = subparsers.add_parser("run", help="Run ingestion pipeline and produce digest")
    run_cmd.add_argument("--config", default="config/default_feeds.json", help="Path to sources config")
    run_cmd.add_argument("--db", default="data/sentinel.db", help="SQLite database path")
    run_cmd.add_argument("--output-dir", default="reports", help="Directory for output digests")
    run_cmd.add_argument("--format", default="terminal,md", help="Comma-separated formats (terminal, md, html)")

    # Command: sources
    subparsers.add_parser("sources", help="List configured feed sources")

    args = parser.parse_args()

    if args.command == "sources" or args.command is None:
        cfg = Path("config/default_feeds.json")
        sources = load_sources(cfg)
        print(f"Configured Sources ({len(sources)}):")
        for s in sources:
            status = "✓ active" if s.enabled else "✗ disabled"
            print(f"- [{s.category}] {s.name} ({s.url}) [{status}]")
        return

    if args.command == "run":
        formats = [f.strip().lower() for f in args.format.split(",")]
        asyncio.run(
            run_pipeline(
                config_path=Path(args.config),
                db_path=Path(args.db),
                output_dir=Path(args.output_dir),
                formats=formats,
            )
        )


if __name__ == "__main__":
    main()
