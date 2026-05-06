from transformers import pipeline


_summarizer = None


def get_summarizer():
    global _summarizer

    if _summarizer is None:
        _summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
        )

    return _summarizer


def summarize_headlines(items, max_items=10):
    texts = [item.text for item in items[:max_items] if item.text]

    if not texts:
        return "No headlines available for summarization."

    combined = ". ".join(texts)

    summarizer = get_summarizer()

    result = summarizer(
        combined,
        max_length=60,
        min_length=20,
        do_sample=False,
    )

    return result[0]["summary_text"]
