from dataclasses import dataclass
from datetime import datetime, timezone

MODEL_ID = "ProsusAI/finbert"

LABEL_TO_SCORE = {
    "positive": 1,
    "neutral": 0,
    "negative": -1,
}

_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        from transformers import pipeline

        print(f"  [Loading FinBERT model: {MODEL_ID} — first run may take a moment]")
        _pipeline = pipeline(
            task="text-classification",
            model=MODEL_ID,
            top_k=None,
            truncation=True,
            max_length=512,
        )
    return _pipeline


@dataclass
class SentimentResult:
    label: str
    score: int
    confidence: float
    all_scores: dict


def score_batch(texts: list[str]) -> list[SentimentResult]:
    clf = _get_pipeline()
    raw_batch = clf(texts)
    results = []
    for raw in raw_batch:
        all_scores = {r["label"]: round(r["score"], 4) for r in raw}
        best = max(raw, key=lambda r: r["score"])
        results.append(
            SentimentResult(
                label=best["label"],
                score=LABEL_TO_SCORE[best["label"]],
                confidence=round(best["score"], 4),
                all_scores=all_scores,
            )
        )
    return results


def compute_recency_weight(published_at: datetime | None, now: datetime) -> float:
    if published_at is None:
        return 0.6

    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)

    delta_hours = max(0.0, (now - published_at).total_seconds() / 3600)

    if delta_hours <= 24:
        return 1.0
    if delta_hours <= 72:
        return 0.75
    if delta_hours <= 168:
        return 0.5
    return 0.25


def compute_confidence_weight(confidence: float) -> float:
    return max(0.35, min(1.0, confidence))


def compute_item_weight(result: SentimentResult, published_at: datetime | None, now: datetime) -> float:
    return compute_recency_weight(published_at, now) * compute_confidence_weight(result.confidence)


def weighted_average(results: list[SentimentResult], items: list, now=None) -> float:
    now = now or datetime.now(timezone.utc)
    weighted_sum = 0.0
    weight_total = 0.0

    for result, item in zip(results, items):
        weight = compute_item_weight(result, getattr(item, "published_at", None), now)
        weighted_sum += result.score * weight
        weight_total += weight

    return weighted_sum / weight_total if weight_total else 0.0
