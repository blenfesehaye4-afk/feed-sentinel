"""Unit tests for FeedParser."""

from datetime import datetime
from feed_sentinel.models import FeedSource
from feed_sentinel.parser import FeedParser

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Sample Dev Feed</title>
    <link>https://example.com</link>
    <description>Tech news</description>
    <item>
      <title>Python 3.13 Released with Faster JIT</title>
      <link>https://example.com/python-313</link>
      <pubDate>Mon, 07 Oct 2024 12:00:00 +0000</pubDate>
      <description>&lt;p&gt;The Python team is proud to announce the &lt;b&gt;release&lt;/b&gt; of Python 3.13.&lt;/p&gt;</description>
      <author>Guido</author>
    </item>
  </channel>
</rss>
"""

SAMPLE_ATOM = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Engineering Feed</title>
  <entry>
    <title>Scaling Microservices with Kafka</title>
    <link href="https://example.com/kafka-scaling"/>
    <published>2024-10-01T15:30:00Z</published>
    <summary>A detailed walkthrough of Kafka event-driven pipelines.</summary>
    <author><name>DevOps Team</name></author>
  </entry>
</feed>
"""

def test_clean_html():
    raw = "<p>Hello <b>world</b>! Click <a href='#'>here</a>.</p>"
    clean = FeedParser.clean_html(raw)
    assert clean == "Hello world! Click here."


def test_parse_rss():
    src = FeedSource(id="test_src", name="Test News", url="https://example.com/rss")
    articles = FeedParser.parse(src, SAMPLE_RSS)
    assert len(articles) == 1
    art = articles[0]
    assert art.title == "Python 3.13 Released with Faster JIT"
    assert art.url == "https://example.com/python-313"
    assert "release of Python 3.13" in art.summary
    assert art.source_name == "Test News"


def test_parse_atom():
    src = FeedSource(id="atom_src", name="Atom News", url="https://example.com/atom")
    articles = FeedParser.parse(src, SAMPLE_ATOM)
    assert len(articles) == 1
    art = articles[0]
    assert art.title == "Scaling Microservices with Kafka"
    assert art.url == "https://example.com/kafka-scaling"
    assert "DevOps Team" in art.author
