"""XML Feed parser for RSS 2.0 and Atom feeds."""

import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Optional

from bs4 import BeautifulSoup

from .models import Article, FeedSource


class FeedParser:
    """Parses RSS/Atom XML payloads into standardized Article models."""

    @staticmethod
    def clean_html(raw_html: str) -> str:
        """Strip HTML tags and normalize whitespace."""
        if not raw_html:
            return ""
        soup = BeautifulSoup(raw_html, "html.parser")
        text = soup.get_text()
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def parse_date(date_str: Optional[str]) -> datetime:
        """Attempt parsing various RSS/Atom date formats."""
        if not date_str:
            return datetime.now(timezone.utc)
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            pass

        # Try ISO format
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            pass

        return datetime.now(timezone.utc)

    @classmethod
    def parse(cls, source: FeedSource, raw_xml: str) -> List[Article]:
        """Parse XML string into List[Article]."""
        articles: List[Article] = []
        if not raw_xml or not raw_xml.strip():
            return articles

        try:
            # Strip potential namespace prefixes for easier XPath querying
            clean_xml = re.sub(r'\sxmlns(:\w+)?="[^"]+"', '', raw_xml, count=1)
            root = ET.fromstring(clean_xml)
        except ET.ParseError:
            # Fallback if XML is malformed
            return articles

        # Check for RSS <item> tags
        items = root.findall(".//item")
        if items:
            for item in items:
                title = (item.findtext("title") or "Untitled").strip()
                link = (item.findtext("link") or "").strip()
                pub_date = cls.parse_date(item.findtext("pubDate"))
                desc = item.findtext("description") or ""
                summary = cls.clean_html(desc)
                author = item.findtext("author") or item.findtext("dc:creator") or source.name

                art_id = hashlib.sha256((link or title).encode("utf-8")).hexdigest()[:16]
                articles.append(
                    Article(
                        id=f"art_{art_id}",
                        source_name=source.name,
                        title=title,
                        url=link,
                        published_at=pub_date,
                        summary=summary[:300] + ("..." if len(summary) > 300 else ""),
                        content=summary,
                        author=author,
                        category=source.category,
                    )
                )
            return articles

        # Check for Atom <entry> tags
        entries = root.findall(".//entry")
        for entry in entries:
            title = (entry.findtext("title") or "Untitled").strip()
            link_elem = entry.find("link")
            link = ""
            if link_elem is not None:
                link = link_elem.get("href") or link_elem.text or ""

            pub_str = entry.findtext("published") or entry.findtext("updated")
            pub_date = cls.parse_date(pub_str)
            summary_raw = entry.findtext("summary") or entry.findtext("content") or ""
            summary = cls.clean_html(summary_raw)
            author = entry.findtext(".//author/name") or source.name

            art_id = hashlib.sha256((link or title).encode("utf-8")).hexdigest()[:16]
            articles.append(
                Article(
                    id=f"art_{art_id}",
                    source_name=source.name,
                    title=title,
                    url=link,
                    published_at=pub_date,
                    summary=summary[:300] + ("..." if len(summary) > 300 else ""),
                    content=summary,
                    author=author,
                    category=source.category,
                )
            )

        return articles
