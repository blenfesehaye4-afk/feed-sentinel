"""Natural language processing: trend detection, keywords, reading time, and sentiment scoring."""

import math
import re
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

from .models import Article, TrendMetric

# Curated lightweight stopwords
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "new", "via", "using", "first", "also", "one", "two",
}

POSITIVE_LEXICON = {
    "breakthrough", "launch", "improve", "improvement", "success", "innovative",
    "efficient", "speedup", "release", "milestone", "boost", "growth", "smart",
    "secure", "win", "solution", "advancement", "powerful", "upgrade", "feat"
}

NEGATIVE_LEXICON = {
    "vulnerability", "breach", "exploit", "outage", "leak", "failure", "fail",
    "bug", "crash", "attack", "risk", "critical", "warning", "flaw", "down",
    "loss", "threat", "severe", "malware", "compromised"
}


class TrendAnalyzer:
    """Extracts top keywords, sentiment polarity, reading duration, and emerging trends."""

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Normalize text and extract lowercase alphanumeric words."""
        cleaned = re.sub(r"[^a-zA-Z0-9\s-]", " ", text.lower())
        tokens = [t for t in cleaned.split() if len(t) > 2 and t not in STOPWORDS]
        return tokens

    @staticmethod
    def estimate_reading_time(text: str) -> int:
        """Estimate reading time in minutes (assuming ~200 WPM average reading speed)."""
        words = len(text.split())
        return max(1, math.ceil(words / 200))

    @staticmethod
    def sentiment_label(score: float) -> str:
        """Categorize sentiment polarity score into human-friendly tag."""
        if score >= 0.15:
            return "positive"
        elif score <= -0.15:
            return "negative"
        return "neutral"

    @classmethod
    def compute_sentiment(cls, text: str) -> float:
        """Compute basic sentiment polarity score between -1.0 and +1.0."""
        tokens = cls.tokenize(text)
        if not tokens:
            return 0.0

        pos_count = sum(1 for t in tokens if t in POSITIVE_LEXICON)
        neg_count = sum(1 for t in tokens if t in NEGATIVE_LEXICON)

        diff = pos_count - neg_count
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        return round(diff / total, 2)

    @classmethod
    def enrich_articles(cls, articles: List[Article]) -> List[Article]:
        """Compute keywords and sentiment for each article."""
        for art in articles:
            combined_text = f"{art.title} {art.summary}"
            tokens = cls.tokenize(combined_text)
            counts = Counter(tokens)
            art.keywords = [w for w, _ in counts.most_common(5)]
            art.sentiment_score = cls.compute_sentiment(combined_text)
        return articles

    @classmethod
    def extract_top_trends(cls, articles: List[Article], top_n: int = 8) -> List[TrendMetric]:
        """Calculate high-frequency terms across the article corpus."""
        if not articles:
            return []

        word_doc_freq = defaultdict(int)
        word_sentiment_list = defaultdict(list)
        word_headlines = defaultdict(list)

        for art in articles:
            seen_in_doc = set(cls.tokenize(f"{art.title} {art.summary}"))
            for word in seen_in_doc:
                word_doc_freq[word] += 1
                word_sentiment_list[word].append(art.sentiment_score)
                if len(word_headlines[word]) < 3:
                    word_headlines[word].append(art.title)

        ranked = sorted(
            word_doc_freq.items(),
            key=lambda item: (item[1], -len(item[0])),
            reverse=True,
        )

        trends = []
        for word, count in ranked[:top_n]:
            sentiments = word_sentiment_list[word]
            avg_sent = round(sum(sentiments) / len(sentiments), 2) if sentiments else 0.0
            trends.append(
                TrendMetric(
                    keyword=word,
                    frequency=count,
                    sentiment_avg=avg_sent,
                    sample_headlines=word_headlines[word],
                )
            )

        return trends
