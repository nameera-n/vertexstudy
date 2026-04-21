from datetime import datetime, timedelta, timezone
from scraper import NewsItem, fetch_headlines
from scraper_url import fetch_headlines_from_url
from scorer import SentimentResult, score_batch, weighted_average

SCORE_LABELS = {
     1: "POSITIVE (+1)",
     0: "NEUTRAL  ( 0)",
    -1: "NEGATIVE (-1)",
}


def parse_window(arg: str):
    try:
        if arg.endswith("h"):
            return timedelta(hours=int(arg[:-1]))
        if arg.endswith("d"):
            return timedelta(days=int(arg[:-1]))
    except Exception:
        pass
    raise ValueError("Invalid window format. Use formats like 24h or 7d.")


def filter_by_time(items, window, now=None):
    if not window:
        return items

    now = now or datetime.now(timezone.utc)
    filtered = []

    for item in items:
        if item.published_at is None:
            filtered.append(item)
            continue

        if now - item.published_at <= window:
            filtered.append(item)

    return filtered


def infer_label_from_score(score: float) -> tuple[str, int]:
    if score > 0.1:
        return "positive", 1
    if score < -0.1:
        return "negative", -1
    return "neutral", 0


def aggregate_article_sentiment(sentence_items: list[NewsItem], sentence_results: list[SentimentResult]):
    if not sentence_items or not sentence_results:
        return [], []

    avg_score = sum(result.score for result in sentence_results) / len(sentence_results)
    avg_confidence = sum(result.confidence for result in sentence_results) / len(sentence_results)

    avg_all_scores = {
        "positive": round(sum(r.all_scores.get("positive", 0) for r in sentence_results) / len(sentence_results), 4),
        "neutral": round(sum(r.all_scores.get("neutral", 0) for r in sentence_results) / len(sentence_results), 4),
        "negative": round(sum(r.all_scores.get("negative", 0) for r in sentence_results) / len(sentence_results), 4),
    }

    label, score = infer_label_from_score(avg_score)
    preview = sentence_items[0].text if sentence_items else "Article"
    if len(preview) > 90:
        preview = preview[:87] + "..."
    article_text = f"Article summary from {len(sentence_items)} sentence(s): {preview}"

    article_item = NewsItem(text=article_text, published_at=sentence_items[0].published_at)
    article_result = SentimentResult(
        label=label,
        score=score,
        confidence=round(avg_confidence, 4),
        all_scores=avg_all_scores,
    )
    return [article_item], [article_result]


def summarize_counts(results: list[SentimentResult]):
    scores = [r.score for r in results]
    total = len(scores)
    pos = scores.count(1)
    neu = scores.count(0)
    neg = scores.count(-1)
    avg_conf = sum(r.confidence for r in results) / total if total else 0.0
    return {
        "total": total,
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "avg_confidence": avg_conf,
    }


def print_results(items, results, title, fetched_count=None):
    print(f"\n{'='*72}")
    print(f"  FinBERT Sentiment Analysis — {title}")
    print(f"{'='*72}\n")

    for item, result in zip(items, results):
        label_str = SCORE_LABELS[result.score]
        conf_str = f"{result.confidence * 100:.1f}%"
        display = item.text if len(item.text) <= 110 else item.text[:107] + "..."

        print(f"  [{label_str}] conf={conf_str:<6}")
        print(f'   "{display}"')
        print()

    avg = weighted_average(results, items)
    overall = "POSITIVE" if avg > 0.1 else ("NEGATIVE" if avg < -0.1 else "NEUTRAL")
    counts = summarize_counts(results)
    dated_count = sum(1 for item in items if item.published_at is not None)
    undated_count = len(items) - dated_count

    print(f"{'─'*72}")
    if fetched_count is not None:
        print(f"  Items analyzed     : {len(results)} of {fetched_count}")
    else:
        print(f"  Items analyzed     : {len(results)}")
    print(f"  Positive (+1)      : {counts['positive']}")
    print(f"  Neutral  ( 0)      : {counts['neutral']}")
    print(f"  Negative (-1)      : {counts['negative']}")
    print(f"  Avg confidence     : {counts['avg_confidence'] * 100:.1f}%")
    print(f"  Dated items        : {dated_count}")
    print(f"  Undated items      : {undated_count}")
    print(f"  Weighted score     : {avg:+.3f}")
    print(f"  Overall sentiment  : {overall}")
    print(f"{'='*72}\n")


def analyze_ticker(ticker: str, window):
    fetched_items = fetch_headlines(ticker)
    items = filter_by_time(fetched_items, window)

    texts = [i.text for i in items]
    results = score_batch(texts) if texts else []

    print_results(items, results, f"{ticker.upper()}", fetched_count=len(fetched_items))


def analyze_url(url: str, window):
    fetched_items = fetch_headlines_from_url(url)
    filtered_items = filter_by_time(fetched_items, window)

    texts = [i.text for i in filtered_items]
    sentence_results = score_batch(texts) if texts else []
    article_items, article_results = aggregate_article_sentiment(filtered_items, sentence_results)

    print_results(article_items, article_results, "URL", fetched_count=len(fetched_items))
