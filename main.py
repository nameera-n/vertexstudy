import sys
from datetime import datetime, timedelta, timezone
from scraper import fetch_headlines
from scraper_url import fetch_headlines_from_url
from scorer import score_batch, weighted_average

SCORE_LABELS = {
     1: "POSITIVE (+1)",
     0: "NEUTRAL  ( 0)",
    -1: "NEGATIVE (-1)",
}


def is_url(arg: str) -> bool:
    return arg.startswith("http://") or arg.startswith("https://")


def parse_window(arg: str):
    if arg.endswith("h"):
        return timedelta(hours=int(arg[:-1]))
    if arg.endswith("d"):
        return timedelta(days=int(arg[:-1]))
    return None


def filter_by_time(items, window):
    if not window:
        return items

    now = datetime.now(timezone.utc)
    filtered = []

    for item in items:
        if item.published_at is None:
            filtered.append(item)
            continue

        if now - item.published_at <= window:
            filtered.append(item)

    return filtered


def print_results(items, results, title):
    print(f"\n{'='*72}")
    print(f"  FinBERT Sentiment Analysis — {title}")
    print(f"{'='*72}\n")

    for item, result in zip(items, results):
        label_str = SCORE_LABELS[result.score]
        conf_str  = f"{result.confidence * 100:.1f}%"
        display = item.text if len(item.text) <= 110 else item.text[:107] + "..."

        print(f"  [{label_str}] conf={conf_str:<6}")
        print(f"   \"{display}\"")
        print()

    avg = weighted_average(results, items)

    overall  = "POSITIVE" if avg > 0.1 else ("NEGATIVE" if avg < -0.1 else "NEUTRAL")

    print(f"{'─'*72}")
    print(f"  Items analyzed     : {len(results)}")
    print(f"  Weighted score     : {avg:+.3f}")
    print(f"  Overall sentiment  : {overall}")
    print(f"{'='*72}\n")


def analyze_ticker(ticker: str, window):
    items = fetch_headlines(ticker)
    items = filter_by_time(items, window)

    texts = [i.text for i in items]
    results = score_batch(texts)

    print_results(items, results, f"{ticker.upper()}")


def analyze_url(url: str):
    texts = fetch_headlines_from_url(url)
    results = score_batch(texts)

    items = [{"text": t, "published_at": None} for t in texts]

    print_results(items, results, "URL")


if __name__ == "__main__":
    args = sys.argv[1:]

    window = None
    clean_args = []

    for arg in args:
        if arg.startswith("--window="):
            window = parse_window(arg.split("=")[1])
        else:
            clean_args.append(arg)

    if not clean_args:
        print("Usage:")
        print("  python3 main.py TSLA --window=24h")
        sys.exit(1)

    for arg in clean_args:
        if is_url(arg):
            analyze_url(arg)
        else:
            analyze_ticker(arg, window)
