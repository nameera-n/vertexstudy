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


def build_analysis_payload(items, results, title, fetched_count=None):
    avg = weighted_average(results, items) if results else 0.0
    overall = "POSITIVE" if avg > 0.1 else ("NEGATIVE" if avg < -0.1 else "NEUTRAL")
    counts = summarize_counts(results)
    dated_count = sum(1 for item in items if item.published_at is not None)
    undated_count = len(items) - dated_count

    return {
        "title": title,
        "items_analyzed": len(results),
        "items_fetched": fetched_count if fetched_count is not None else len(results),
        "counts": counts,
        "dated_items": dated_count,
        "undated_items": undated_count,
        "weighted_score": round(avg, 4),
        "overall_sentiment": overall,
        "items": [
            {
                "text": item.text,
                "published_at": item.published_at.isoformat() if item.published_at else None,
                "label": result.label,
                "score": result.score,
                "confidence": result.confidence,
                "all_scores": result.all_scores,
            }
            for item, result in zip(items, results)
        ],
    }


def print_results(items, results, title, fetched_count=None):
    payload = build_analysis_payload(items, results, title, fetched_count=fetched_count)

    print(f"\n{'='*72}")
    print(f"  FinBERT Sentiment Analysis — {title}")
    print(f"{'='*72}\n")

    for entry in payload["items"]:
        label_str = SCORE_LABELS[entry["score"]]
        conf_str = f"{entry['confidence'] * 100:.1f}%"
        display = entry["text"] if len(entry["text"]) <= 110 else entry["text"][:107] + "..."

        print(f"  [{label_str}] conf={conf_str:<6}")
        print(f'   "{display}"')
        print()

    print(f"{'─'*72}")
    print(f"  Items analyzed     : {payload['items_analyzed']} of {payload['items_fetched']}")
    print(f"  Positive (+1)      : {payload['counts']['positive']}")
    print(f"  Neutral  ( 0)      : {payload['counts']['neutral']}")
    print(f"  Negative (-1)      : {payload['counts']['negative']}")
    print(f"  Avg confidence     : {payload['counts']['avg_confidence'] * 100:.1f}%")
    print(f"  Dated items        : {payload['dated_items']}")
    print(f"  Undated items      : {payload['undated_items']}")
    print(f"  Weighted score     : {payload['weighted_score']:+.3f}")
    print(f"  Overall sentiment  : {payload['overall_sentiment']}")
    print(f"{'='*72}\n")

    return payload


def analyze_ticker(ticker: str, window, output_mode="print"):
    fetched_items = fetch_headlines(ticker)
    items = filter_by_time(fetched_items, window)

    texts = [i.text for i in items]
    results = score_batch(texts) if texts else []

    title = f"{ticker.upper()}"
    if output_mode == "data":
        return build_analysis_payload(items, results, title, fetched_count=len(fetched_items))
    return print_results(items, results, title, fetched_count=len(fetched_items))


def analyze_url(url: str, window, output_mode="print"):
    fetched_items = fetch_headlines_from_url(url)
    filtered_items = filter_by_time(fetched_items, window)

    texts = [i.text for i in filtered_items]
    sentence_results = score_batch(texts) if texts else []
    article_items, article_results = aggregate_article_sentiment(filtered_items, sentence_results)

    title = "URL"
    if output_mode == "data":
        return build_analysis_payload(article_items, article_results, title, fetched_count=len(fetched_items))
    return print_results(article_items, article_results, title, fetched_count=len(fetched_items))
