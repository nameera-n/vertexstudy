from pathlib import Path
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bs4 import BeautifulSoup
from scraper import NewsItem
from scraper_url import extract_publish_date
from scorer import SentimentResult, compute_recency_weight, compute_confidence_weight, weighted_average
from main import parse_window, filter_by_time


NOW = datetime(2026, 4, 20, 12, 0, 0, tzinfo=timezone.utc)


def make_result(score: int, confidence: float) -> SentimentResult:
    label_map = {1: "positive", 0: "neutral", -1: "negative"}
    return SentimentResult(
        label=label_map[score],
        score=score,
        confidence=confidence,
        all_scores={},
    )


def test_parse_window_hours():
    assert parse_window("24h") == timedelta(hours=24)


def test_parse_window_days():
    assert parse_window("7d") == timedelta(days=7)


def test_filter_by_time_keeps_recent_items():
    items = [
        NewsItem(text="recent", published_at=NOW - timedelta(hours=6)),
        NewsItem(text="old", published_at=NOW - timedelta(days=10)),
    ]

    filtered = filter_by_time(items, timedelta(days=3), now=NOW)
    assert [item.text for item in filtered] == ["recent"]


def test_filter_by_time_keeps_undated_items():
    items = [
        NewsItem(text="undated", published_at=None),
        NewsItem(text="recent", published_at=NOW - timedelta(hours=4)),
    ]

    filtered = filter_by_time(items, timedelta(days=1), now=NOW)
    assert [item.text for item in filtered] == ["undated", "recent"]


def test_recency_weight_ordering():
    newest = compute_recency_weight(NOW - timedelta(hours=3), NOW)
    mid = compute_recency_weight(NOW - timedelta(days=2), NOW)
    old = compute_recency_weight(NOW - timedelta(days=10), NOW)

    assert newest > mid > old


def test_confidence_weight_has_floor_and_cap():
    assert compute_confidence_weight(0.1) == 0.35
    assert compute_confidence_weight(0.8) == 0.8
    assert compute_confidence_weight(1.5) == 1.0


def test_weighted_average_favors_recent_confident_item():
    items = [
        NewsItem(text="fresh positive", published_at=NOW - timedelta(hours=2)),
        NewsItem(text="old negative", published_at=NOW - timedelta(days=10)),
    ]
    results = [
        make_result(1, 0.95),
        make_result(-1, 0.40),
    ]

    avg = weighted_average(results, items, now=NOW)
    assert avg > 0


def test_extract_publish_date_from_meta():
    html = '''
    <html><head>
        <meta property="article:published_time" content="2026-04-19T14:22:00Z" />
    </head><body></body></html>
    '''
    soup = BeautifulSoup(html, "lxml")
    parsed = extract_publish_date(soup)

    assert parsed is not None
    assert parsed.year == 2026
    assert parsed.month == 4
    assert parsed.day == 19


def test_extract_publish_date_from_json_ld():
    html = '''
    <html><head>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "datePublished": "2026-04-18T09:15:00Z"
        }
        </script>
    </head><body></body></html>
    '''
    soup = BeautifulSoup(html, "lxml")
    parsed = extract_publish_date(soup)

    assert parsed is not None
    assert parsed.year == 2026
    assert parsed.month == 4
    assert parsed.day == 18
