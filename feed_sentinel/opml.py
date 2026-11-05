"""OPML (Outline Processor Markup Language) import and export utility for RSS feeds."""

from __future__ import annotations
import uuid
import xml.etree.ElementTree as ET
from typing import Sequence
from .models import FeedSource


def import_opml(opml_xml: str) -> list[FeedSource]:
    """Parse an OPML XML string and extract FeedSource objects."""
    root = ET.fromstring(opml_xml)
    sources: list[FeedSource] = []

    # Find outlines in body
    for outline in root.findall(".//outline"):
        xml_url = outline.get("xmlUrl") or outline.get("xmlurl")
        if xml_url:
            name = outline.get("text") or outline.get("title") or "Unnamed Feed"
            category = outline.get("category") or "general"
            feed_id = outline.get("id") or f"src_{uuid.uuid4().hex[:8]}"

            sources.append(
                FeedSource(
                    id=feed_id,
                    name=name,
                    url=xml_url,
                    category=category,
                    enabled=True,
                )
            )

    return sources


def export_opml(sources: Sequence[FeedSource], title: str = "Feed Sentinel Feeds") -> str:
    """Generate OPML 2.0 XML from a collection of FeedSource objects."""
    root = ET.Element("opml", version="2.0")
    head = ET.SubElement(root, "head")
    title_el = ET.SubElement(head, "title")
    title_el.text = title

    body = ET.SubElement(root, "body")

    # Group by category if possible
    categories: dict[str, list[FeedSource]] = {}
    for s in sources:
        cat = s.category or "general"
        categories.setdefault(cat, []).append(s)

    for cat_name, cat_sources in categories.items():
        cat_outline = ET.SubElement(body, "outline", text=cat_name.title())
        for s in cat_sources:
            ET.SubElement(
                cat_outline,
                "outline",
                text=s.name,
                title=s.name,
                type="rss",
                xmlUrl=s.url,
                category=s.category,
            )

    return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
