import sys
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from xml.etree import ElementTree

def _fetch_rss(ticker: str) -> list:
    url = f"https://finance.yahoo.com/rss/headline?s={urllib.parse.quote(ticker)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml = resp.read()
        root = ElementTree.fromstring(xml)
        titles = [item.findtext("title") for item in root.iter("item")]
        return [t.strip() for t in titles if t and t.strip()]
    except Exception:
        return []


class HeadlineParser(HTMLParser):
    """Extracts headline text from <h3> tags in Yahoo Finance HTML."""

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


def _fetch_html(ticker: str) -> list:
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
                return parser.headlines
        except Exception:
            continue
    return []


def fetch_headlines(ticker: str) -> list:
    """
    Fetch and deduplicate news headlines for a ticker.
    Tries RSS first, falls back to HTML scraping.
    """
    ticker = ticker.upper()

    print(f"  [Fetching headlines for {ticker} via RSS...]")
    headlines = _fetch_rss(ticker)

    if not headlines:
        print(f"  [RSS empty, falling back to HTML scrape...]")
        headlines = _fetch_html(ticker)

    if not headlines:
        print(f"[ERROR] Could not retrieve headlines for {ticker}.")
        print("        Yahoo Finance may be blocking requests or has changed its structure.")
        sys.exit(1)
    seen = set()
    unique = []
    for h in headlines:
        if h not in seen:
            seen.add(h)
            unique.append(h)

    print(f"  [Found {len(unique)} headlines]\n")
    return unique