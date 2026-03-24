import sys
import re
import urllib.request
from bs4 import BeautifulSoup


BODY_TAGS = ["article", "main", "section"]

BODY_CLASSES = [
    # Generic
    "article", "article-body", "article-content", "article__body",
    "article__content", "post-body", "post-content", "story-body",
    "story-content", "entry-content", "content-body",
    # Yahoo Finance
    "caas-body",
    # Reuters
    "article-body__content",
    # CNBC
    "ArticleBody-articleBody",
    # Bloomberg
    "body-content",
]
STRIP_TAGS = [
    "script", "style", "noscript", "nav", "header", "footer",
    "aside", "figure", "figcaption", "iframe", "form", "button",
    "svg", "img", "picture", "video", "audio", "ads", "advertisement",
]


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


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

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

def _split_sentences(text: str) -> list:
    text = re.sub(r"\s+", " ", text).strip()
    raw = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)

    sentences = []
    for s in raw:
        s = s.strip()
        
        words = s.split()
        if len(s) >= 30 and len(words) >= 5 and re.search(r"[a-zA-Z]{3,}", s):
            sentences.append(s)

    return sentences


def fetch_sentences(url: str) -> list:
    """
    Fetch a news article from any URL and return a list of clean sentences
    suitable for FinBERT sentiment scoring.
    """
    print(f"  [Fetching article...]")
    html = _fetch_html(url)

    print(f"  [Parsing article body...]")
    text = _extract_text(html)

    sentences = _split_sentences(text)

    if not sentences:
        print("[ERROR] Could not extract readable sentences from the page.")
        print("        The page may be paywalled, JS-rendered, or structured unusually.")
        sys.exit(1)

    print(f"  [Extracted {len(sentences)} sentences]\n")
    return sentences

fetch_headlines_from_url = fetch_sentences