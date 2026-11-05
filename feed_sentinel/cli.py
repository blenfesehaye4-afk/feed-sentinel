"""CLI commands for Feed Sentinel."""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .fetcher import FeedFetcher
from .generator import ReportGenerator
from .models import FeedSource, PipelineResult
from .nlp import TrendAnalyzer
from .notifier import WebhookNotifier
from .opml import export_opml, import_opml
from .parser import FeedParser
from .storage import ArticleStorage


def load_sources(config_path: Path) -> List[FeedSource]:
    """Load feed sources from JSON configuration."""
    if not config_path.exists():
        return [
            FeedSource(id="github", name="GitHub Blog", url="https://github.blog/engineering/feed/", category="engineering"),
            FeedSource(id="python", name="Python Insider", url="https://pythoninsider.blogspot.com/feeds/posts/default", category="python"),
        ]

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [FeedSource(**item) for item in data]


def save_sources(config_path: Path, sources: List[FeedSource]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        data = [
            {
                "id": s.id,
                "name": s.name,
                "url": s.url,
                "category": s.category,
                "enabled": s.enabled,
            }
            for s in sources
        ]
        json.dump(data, f, indent=2)


async def run_pipeline(
    config_path: Path,
    db_path: Path,
    output_dir: Path,
    formats: List[str],
    notify_url: Optional[str] = None,
) -> PipelineResult:
    """Execute ingestion, NLP analysis, storage, report generation, and notifications."""
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

    # 7. Webhook notification
    if notify_url:
        notifier = WebhookNotifier(webhook_url=notify_url)
        try:
            success = await notifier.send_async(result)
            if success:
                print(f"Webhook notification delivered to {notify_url}")
            else:
                print(f"Webhook notification returned non-success response")
        except Exception as e:
            print(f"Failed to deliver webhook notification: {e}")

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
    run_cmd.add_argument("--notify", default=None, help="Webhook URL for trend alerts")

    # Command: sources
    subparsers.add_parser("sources", help="List configured feed sources")

    # Command: opml
    opml_cmd = subparsers.add_parser("opml", help="Import or export feed subscriptions in OPML format")
    opml_sub = opml_cmd.add_subparsers(dest="opml_action", required=True)

    opml_import = opml_sub.add_parser("import", help="Import feeds from an OPML file")
    opml_import.add_argument("file", help="Path to OPML XML file")
    opml_import.add_argument("--config", default="config/default_feeds.json", help="Target config JSON")

    opml_export = opml_sub.add_parser("export", help="Export feeds to OPML XML format")
    opml_export.add_argument("-o", "--output", default=None, help="Output OPML file path (default stdout)")
    opml_export.add_argument("--config", default="config/default_feeds.json", help="Sources config JSON")

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
                notify_url=args.notify,
            )
        )
        return

    if args.command == "opml":
        cfg = Path(args.config)
        if args.opml_action == "import":
            with open(args.file, "r", encoding="utf-8") as f:
                new_sources = import_opml(f.read())
            existing = {s.url: s for s in load_sources(cfg)}
            for ns in new_sources:
                existing[ns.url] = ns
            save_sources(cfg, list(existing.values()))
            print(f"Imported {len(new_sources)} feeds into {cfg}")
        elif args.opml_action == "export":
            sources = load_sources(cfg)
            xml_str = export_opml(sources)
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(xml_str)
                print(f"Exported {len(sources)} feeds to {args.output}")
            else:
                print(xml_str)


if __name__ == "__main__":
    main()
