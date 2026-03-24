"""
Using FinBERT to score the sentiment of financial text.

If running locally, make sure to install the required dependencies first:
    pip install transformers torch sentencepiece
    """

from dataclasses import dataclass
from transformers import pipeline

MODEL_ID = "ProsusAI/finbert"

LABEL_TO_SCORE = {
    "positive":  1,
    "neutral":   0,
    "negative": -1,
}

_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
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
    label:      str
    score:      int
    confidence: float
    all_scores: dict


def score_text(text: str) -> SentimentResult:
    """Run FinBERT on a single string and return a SentimentResult."""
    clf = _get_pipeline()
    raw = clf(text)[0]
    all_scores = {r["label"]: round(r["score"], 4) for r in raw}
    best = max(raw, key=lambda r: r["score"])
    return SentimentResult(
        label=best["label"],
        score=LABEL_TO_SCORE[best["label"]],
        confidence=round(best["score"], 4),
        all_scores=all_scores,
    )


def score_batch(texts: list) -> list:
    """Run FinBERT on a list of strings in a single batched inference call."""
    clf = _get_pipeline()
    raw_batch = clf(texts)
    results = []
    for raw in raw_batch:
        all_scores = {r["label"]: round(r["score"], 4) for r in raw}
        best = max(raw, key=lambda r: r["score"])
        results.append(SentimentResult(
            label=best["label"],
            score=LABEL_TO_SCORE[best["label"]],
            confidence=round(best["score"], 4),
            all_scores=all_scores,
        ))
    return results