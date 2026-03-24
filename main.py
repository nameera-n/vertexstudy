import sys
from scraper import fetch_headlines
from scraper_url import fetch_headlines_from_url
from scorer import score_batch

SCORE_LABELS = {
     1: "POSITIVE (+1)",
     0: "NEUTRAL  ( 0)",
    -1: "NEGATIVE (-1)",
}


def is_url(arg: str) -> bool:
    return arg.startswith("http://") or arg.startswith("https://")


def print_results(headlines: list, results: list, title: str):
    print(f"\n{'='*72}")
    print(f"  FinBERT Sentiment Analysis — {title}")
    print(f"{'='*72}\n")

    for headline, result in zip(headlines, results):
        label_str = SCORE_LABELS[result.score]
        conf_str  = f"{result.confidence * 100:.1f}%"
        s = result.all_scores
        breakdown = (
            f"pos={s.get('positive', 0)*100:.0f}% "
            f"neu={s.get('neutral',  0)*100:.0f}% "
            f"neg={s.get('negative', 0)*100:.0f}%"
        )
        display = headline if len(headline) <= 110 else headline[:107] + "..."
        print(f"  [{label_str}] conf={conf_str:<6}  ({breakdown})")
        print(f"   \"{display}\"")
        print()

    scores   = [r.score for r in results]
    total    = len(scores)
    pos      = scores.count(1)
    neu      = scores.count(0)
    neg      = scores.count(-1)
    avg      = sum(scores) / total if total else 0
    avg_conf = sum(r.confidence for r in results) / total if total else 0
    overall  = "POSITIVE" if avg > 0.1 else ("NEGATIVE" if avg < -0.1 else "NEUTRAL")

    print(f"{'─'*72}")
    print(f"  Model              : ProsusAI/finbert")
    print(f"  Items analyzed     : {total}")
    print(f"  Positive (+1)      : {pos}  ({pos/total*100:.1f}%)")
    print(f"  Neutral  ( 0)      : {neu}  ({neu/total*100:.1f}%)")
    print(f"  Negative (-1)      : {neg}  ({neg/total*100:.1f}%)")
    print(f"  Average score      : {avg:+.3f}")
    print(f"  Avg confidence     : {avg_conf*100:.1f}%")
    print(f"  Overall sentiment  : {overall}")
    print(f"{'='*72}\n")


def analyze_ticker(ticker: str):
    headlines = fetch_headlines(ticker)
    results   = score_batch(headlines)
    print_results(headlines, results, f"{ticker.upper()}  [Yahoo Finance RSS]")


def analyze_url(url: str):
    headlines = fetch_headlines_from_url(url)
    results   = score_batch(headlines)
    # Show a shortened version of the URL as the title
    title = url if len(url) <= 60 else url[:57] + "..."
    print_results(headlines, results, f"URL: {title}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 main.py <TICKER>")
        print("  python3 main.py <YAHOO_FINANCE_URL>")
        print("  python3 main.py TSLA NVDA MSFT")
        sys.exit(1)

    for arg in sys.argv[1:]:
        if is_url(arg):
            analyze_url(arg)
        else:
            analyze_ticker(arg)