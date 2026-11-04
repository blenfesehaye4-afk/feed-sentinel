<div align="center">

# 📡 feed-sentinel

**Intelligent Automated RSS & Web Content Ingestion Pipeline with Trend Analysis**

[![CI](https://github.com/blenfesehaye4-afk/feed-sentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/blenfesehaye4-afk/feed-sentinel/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An asynchronous content ingestion and automated intelligence pipeline that aggregates RSS/Atom streams, deduplicates content via cryptographic hashing, detects emerging topic trends with sentiment heuristics, and outputs executive Markdown, HTML, and terminal digests.

</div>

---

## 🏗️ Architecture & Pipeline Flow

```
   ┌────────────────────────────────────────────────────────┐
   │        Multi-Feed Sources (RSS 2.0 / Atom XML)         │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │         Asynchronous Fetcher (httpx + Concurrency)     │
   │           - Concurrency Semaphore & Rate Limits        │
   │           - Auto-Retries & Custom User-Agents          │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │                 FeedParser Engine                      │
   │           - XML normalization & Tag Stripping          │
   │           - Cross-format ISO/RFC Timestamp Parsing     │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │            NLP & Trend Extraction Layer                │
   │           - Stopword filtering & Frequency Analysis    │
   │           - Sentiment Polarity Index Scoring           │
   │           - Emerging Keyword Ranking                   │
   └───────────────────────────┬────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
   ┌───────────────────────┐       ┌────────────────────────┐
   │ SQLite Storage Engine │       │  Multi-Format Exporter │
   │ - SHA-256 Deduplication│      │  - Rich Terminal UI    │
   │ - Historical Indexing │       │  - Executive Markdown  │
   └───────────────────────┘       │  - Standalone HTML     │
                                   └────────────────────────┘
```

---

## ✨ Key Features

- ⚡ **High-Throughput Async Fetching**: Parallel feed ingestion with configurable concurrency semaphores.
- 🧹 **Robust XML & HTML Cleanser**: Standardizes both RSS 2.0 and Atom feeds, stripping inline tags and normalizing timestamps.
- 🔍 **Automated Deduplication**: Content and URL hashing backed by persistent SQLite storage.
- 📈 **NLP Trend & Sentiment Analytics**: Automatically surfaces spiking keywords and analyzes headline sentiment polarity without heavy external models.
- 📊 **Executive Multi-Format Digests**:
  - Interactive **Rich Terminal** dashboard
  - GitHub-flavored **Markdown** brief
  - Production-ready **HTML** email newsletter

---

## 🚀 Quickstart

### Installation

```bash
git clone https://github.com/blenfesehaye4-afk/feed-sentinel.git
cd feed-sentinel
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Execution

Run the ingestion pipeline and display the terminal dashboard:
```bash
feed-sentinel run
```

Generate both a Markdown report and an HTML newsletter in `./reports`:
```bash
feed-sentinel run --format "terminal,md,html" --output-dir ./reports
```

Inspect configured feeds:
```bash
feed-sentinel sources
```

---

## ⚙️ Configuration (`config/default_feeds.json`)

Customize tracked sources with ease:

```json
[
  {
    "id": "github_blog",
    "name": "GitHub Engineering",
    "url": "https://github.blog/engineering/feed/",
    "category": "engineering",
    "enabled": true
  },
  {
    "id": "python_insider",
    "name": "Python Insider",
    "url": "https://pythoninsider.blogspot.com/feeds/posts/default",
    "category": "python",
    "enabled": true
  }
]
```

---

## ⏰ Automated Scheduling (Cron / Systemd)

Run Feed Sentinel every morning at 08:00 AM via crontab:

```cron
0 8 * * * /path/to/.venv/bin/feed-sentinel run --format "md,html" --output-dir /var/www/reports
```

---

## 🧪 Testing

```bash
pytest -v
```

---

## 📜 License

MIT License © 2026 Blen Fesehaye
