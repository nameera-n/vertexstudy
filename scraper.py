import sys
import urllib.request
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree


@dataclass
class NewsItem:
    text: str
    published_at: datetime | None = None
    url: str | None = None


def _to_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_rss_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return _to_utc(parsedate_to_datetime(value))
    except Exception:
        return None


def _fetch_rss(ticker: str) -> list[NewsItem]:
    url = f"https://finance.yahoo.com/rss/headline?s={urllib.parse.quote(ticker)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml = resp.read()

        root = ElementTree.fromstring(xml)

        items = []

        for item in root.iter("item"):
            title = item.findtext("title")
            link = item.findtext("link")

            if not title or not title.strip():
                continue

            items.append(
                NewsItem(
                    text=title.strip(),
                    published_at=_parse_rss_datetime(item.findtext("pubDate")),
                    url=link,
                )
            )

        return items

    except Exception:
        return []


class HeadlineParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headlines = []
        self._in_h3 = False
        self._current = []

    def handle_starttag(self, tag, attrs):
        if tag == "h3":
            self._in_h3 = True
            self._current = []

    def handle_endtag(self, tag):
        if tag == "h3" and self._in_h3:
            text = "".join(self._current).strip()
            if text:
                self.headlines.append(text)
            self._in_h3 = False

    def handle_data(self, data):
        if self._in_h3:
            self._current.append(data)


def _fetch_html(ticker: str) -> list[NewsItem]:
    urls = [
        f"https://finance.yahoo.com/quote/{urllib.parse.quote(ticker)}/",
        f"https://finance.yahoo.com/quote/{urllib.parse.quote(ticker)}",
    ]

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            parser = HeadlineParser()
            parser.feed(html)

            if parser.headlines:
                return [NewsItem(text=h, url=url) for h in parser.headlines]

        except Exception:
            continue

    return []


def fetch_headlines(ticker: str) -> list[NewsItem]:
    ticker = ticker.upper()

    print(f"  [Fetching headlines for {ticker} via RSS...]")

    items = _fetch_rss(ticker)

    if not items:
        print("  [RSS empty, falling back to HTML scrape...]")
        items = _fetch_html(ticker)

    if not items:
        print(f"[ERROR] Could not retrieve headlines for {ticker}.")
        print("        Yahoo Finance may be blocking requests or has changed its structure.")
        sys.exit(1)

    seen = set()
    unique = []
    dated_count = 0

    for item in items:
        if item.text not in seen:
            seen.add(item.text)
            unique.append(item)

            if item.published_at is not None:
                dated_count += 1

    print(f"  [Found {len(unique)} headlines | dated: {dated_count}]")
    print()

    return unique
