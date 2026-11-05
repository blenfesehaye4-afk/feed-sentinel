from feed_sentinel.models import FeedSource
from feed_sentinel.opml import export_opml, import_opml


def test_opml_export_and_import():
    sources = [
        FeedSource("s1", "TechCrunch", "https://techcrunch.com/feed/", category="tech"),
        FeedSource("s2", "Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", category="tech"),
        FeedSource("s3", "Hacker News", "https://news.ycombinator.com/rss", category="general"),
    ]

    xml = export_opml(sources, title="Test Feeds")
    assert "<opml version=\"2.0\">" in xml
    assert "xmlUrl=\"https://techcrunch.com/feed/\"" in xml

    imported = import_opml(xml)
    assert len(imported) == 3
    urls = [s.url for s in imported]
    assert "https://techcrunch.com/feed/" in urls
    assert "https://news.ycombinator.com/rss" in urls
