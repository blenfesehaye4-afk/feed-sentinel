# 📡 Feed Sentinel

[![CI](https://github.com/blenfesehaye4-afk/feed-sentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/blenfesehaye4-afk/feed-sentinel/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Automated RSS/Atom ingestion, OPML subscription sync, NLP trend detection & webhook alerting engine.**

Feed Sentinel automates intelligence gathering from engineering blogs, technical news feeds, and release announcements. It cleans noisy HTML, extracts emerging keywords across disparate sources, calculates sentiment metrics, estimates reading time, and distributes digests to terminal dashboards, Markdown files, HTML pages, or Slack/Discord webhooks.

---

## 🌟 What's New in v0.2.0

- 📑 **Standard OPML 2.0 Support**: Bulk import and export feed subscriptions to and from your favorite RSS readers (Feedly, NetNewsWire, Inoreader).
- 🔔 **Webhook & Trend Alerting**: Real-time webhook dispatcher (`--notify <webhook_url>`) formatting digests into Slack, Discord, and HTTP sinks.
- ⏱️ **Reading Time & Sentiment Grading**: Automated article reading time estimates and sentiment polarity classification (`positive`, `neutral`, `negative`).

---

## 🏗️ Architecture

```
[ OPML Import / JSON Config ]
             │
             ▼
  ┌──────────────────────┐
  │  Async Feed Fetcher  │ (Concurrent HTTP/2 with httpx)
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │  RSS / Atom Parser   │ (HTML sanitization & text stripping)
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │  NLP & Trend Engine  │ (Stopwords, TF-IDF ranking, Sentiment)
  └──────────┬───────────┘
             │
             ├── SQLite Deduplication Store
             │
             ▼
  ┌────────────────────────────────────────────────────────┐
  │  Multi-Format Distribution & Alerts                     │
  │  • Rich Terminal Dashboard                             │
  │  • Executive Markdown Digests                          │
  │  • Self-contained HTML Reports                         │
  │  • Slack / Discord Webhook Notifications               │
  └────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

```bash
pip install feed-sentinel
```

Or install from source in development mode:

```bash
git clone https://github.com/blenfesehaye4-afk/feed-sentinel.git
cd feed-sentinel
pip install -e .[dev]
```

---

## 💻 CLI Commands

### 1. Ingest Feeds & Generate Executive Digest
```bash
feed-sentinel run --format terminal,md,html
```

### 2. Dispatch Alerts to Discord or Slack
```bash
feed-sentinel run --notify "https://discord.com/api/webhooks/..."
```

### 3. Import & Export OPML Subscriptions
```bash
# Import OPML feeds
feed-sentinel opml import my_subscriptions.opml

# Export feeds to OPML
feed-sentinel opml export -o backup.opml
```

### 4. List Configured Sources
```bash
feed-sentinel sources
```

---

## 🧪 Running Tests

```bash
pytest -v
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
