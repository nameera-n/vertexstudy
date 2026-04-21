import sys
import re
import json
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from scraper import NewsItem


BODY_TAGS = ["article", "main", "section"]

BODY_CLASSES = [
    "article", "article-body", "article-content", "article__body",
    "article__content", "post-body", "post-content", "story-body",
    "story-content", "entry-content", "content-body",
    "caas-body",
    "article-body__content",
    "ArticleBody-articleBody",
    "body-content",
]

STRIP_TAGS = [
    "script", "style", "noscript", "nav", "header", "footer",
    "aside", "figure", "figcaption", "iframe", "form", "button",
    "svg", "img", "picture", "video", "audio", "ads", "advertisement",
]

META_DATE_KEYS = [
    "article:published_time",
    "article:modified_time",
    "og:published_time",
    "publish-date",
    "published_time",
    "pubdate",
    "date",
    "datepublished",
    "dc.date",
    "dc.date.issued",
    "parsely-pub-date",
]


def _to_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_date_string(value: str | None) -> datetime | None:
    if not value:
        return None

    value = value.strip()
    if not value:
        return None

    try:
        return _to_utc(parsedate_to_datetime(value))
    except Exception:
        pass

    iso_candidate = value.replace("Z", "+00:00")
    try:
        return _to_utc(datetime.fromisoformat(iso_candidate))
    except Exception:
        pass

    patterns = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d",
        "%b %d, %Y",
        "%B %d, %Y",
    ]
    for pattern in patterns:
        try:
            return _to_utc(datetime.strptime(value, pattern))
        except Exception:
            continue

    return None


def _fetch_html(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[ERROR] Could not fetch URL: {e}")
        sys.exit(1)


def _extract_text(soup: BeautifulSoup) -> str:
    soup = BeautifulSoup(str(soup), "lxml")

    for tag in soup(STRIP_TAGS):
        tag.decompose()

    body = None
    for cls in BODY_CLASSES:
        body = soup.find(class_=cls)
        if body:
            break

    if not body:
        for tag in BODY_TAGS:
            body = soup.find(tag)
            if body:
                break

    if not body:
        body = soup

    return body.get_text(separator=" ", strip=True)


def _extract_date_from_meta(soup: BeautifulSoup) -> datetime | None:
    for meta in soup.find_all("meta"):
        key = (meta.get("property") or meta.get("name") or meta.get("itemprop") or "").strip().lower()
        content = (meta.get("content") or "").strip()
        if key in META_DATE_KEYS and content:
            parsed = _parse_date_string(content)
            if parsed:
                return parsed
    return None


def _extract_date_from_time_tag(soup: BeautifulSoup) -> datetime | None:
    for tag in soup.find_all("time"):
        candidate = tag.get("datetime") or tag.get_text(" ", strip=True)
        parsed = _parse_date_string(candidate)
        if parsed:
            return parsed
    return None


def _find_date_in_json_ld(obj) -> datetime | None:
    if isinstance(obj, dict):
        for key in ["datePublished", "dateCreated", "uploadDate", "dateModified"]:
            if key in obj:
                parsed = _parse_date_string(str(obj[key]))
                if parsed:
                    return parsed
        for value in obj.values():
            parsed = _find_date_in_json_ld(value)
            if parsed:
                return parsed
    elif isinstance(obj, list):
        for item in obj:
            parsed = _find_date_in_json_ld(item)
            if parsed:
                return parsed
    return None


def _extract_date_from_json_ld(soup: BeautifulSoup) -> datetime | None:
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = tag.string or tag.get_text(strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        parsed = _find_date_in_json_ld(data)
        if parsed:
            return parsed
    return None


def extract_publish_date(soup: BeautifulSoup) -> datetime | None:
    for extractor in [_extract_date_from_meta, _extract_date_from_json_ld, _extract_date_from_time_tag]:
        parsed = extractor(soup)
        if parsed:
            return parsed
    return None


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    raw = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)

    sentences = []
    for s in raw:
        s = s.strip()
        words = s.split()
        if len(s) >= 30 and len(words) >= 5 and re.search(r"[a-zA-Z]{3,}", s):
            sentences.append(s)

    return sentences


def fetch_sentences(url: str) -> list[NewsItem]:
    print("  [Fetching article...]")
    html = _fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    published_at = extract_publish_date(soup)
    if published_at:
        print(f"  [Extracted publish date: {published_at.isoformat()}]")
    else:
        print("  [Publish date not found in page metadata]")

    print("  [Parsing article body...]")
    text = _extract_text(soup)
    sentences = _split_sentences(text)

    if not sentences:
        print("[ERROR] Could not extract readable sentences from the page.")
        print("        The page may be paywalled, JS-rendered, or structured unusually.")
        sys.exit(1)

    print(f"  [Extracted {len(sentences)} sentences]")
    print()
    return [NewsItem(text=s, published_at=published_at) for s in sentences]


fetch_headlines_from_url = fetch_sentences
