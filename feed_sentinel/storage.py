"""SQLite persistence and deduplication storage."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .models import Article


class ArticleStorage:
    """Manages SQLite storage for article history and deduplication."""

    def __init__(self, db_path: str = "sentinel_data.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    source_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE,
                    published_at TEXT,
                    summary TEXT,
                    author TEXT,
                    category TEXT,
                    sentiment_score REAL,
                    created_at TEXT
                )
                """
            )
            conn.commit()

    def store_articles(self, articles: List[Article]) -> int:
        """Insert articles. Skip duplicates. Returns count of newly inserted rows."""
        new_count = 0
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            for art in articles:
                try:
                    conn.execute(
                        """
                        INSERT INTO articles (id, source_name, title, url, published_at, summary, author, category, sentiment_score, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            art.id,
                            art.source_name,
                            art.title,
                            art.url,
                            art.published_at.isoformat(),
                            art.summary,
                            art.author,
                            art.category,
                            art.sentiment_score,
                            now_iso,
                        ),
                    )
                    new_count += 1
                except sqlite3.IntegrityError:
                    # Duplicate article URL or ID already in database
                    continue
            conn.commit()
        return new_count

    def get_recent_articles(self, limit: int = 50) -> List[Article]:
        """Fetch latest articles ordered by publication date."""
        articles = []
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM articles ORDER BY published_at DESC LIMIT ?", (limit,)
            )
            for row in cursor.fetchall():
                try:
                    dt = datetime.fromisoformat(row["published_at"])
                except Exception:
                    dt = datetime.now(timezone.utc)

                articles.append(
                    Article(
                        id=row["id"],
                        source_name=row["source_name"],
                        title=row["title"],
                        url=row["url"],
                        published_at=dt,
                        summary=row["summary"],
                        content=row["summary"],
                        author=row["author"],
                        category=row["category"],
                        sentiment_score=row["sentiment_score"],
                    )
                )
        return articles

    def total_count(self) -> int:
        """Return total article count."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as cnt FROM articles")
            return cursor.fetchone()["cnt"]
