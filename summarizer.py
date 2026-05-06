from transformers import pipeline


_summarizer = None


def get_summarizer():
    global _summarizer

    if _summarizer is None:
        _summarizer = pipeline(
            task="text2text-generation",
            model="google/flan-t5-base",
        )

    return _summarizer


def summarize_headlines(items, max_items=10):
    texts = [item.text for item in items[:max_items] if item.text]

    if not texts:
        return "No headlines available for summarization."

    combined = ". ".join(texts)

    prompt = (
        "Summarize the financial sentiment and key market themes from these headlines: "
        + combined
    )

    summarizer = get_summarizer()

    result = summarizer(
        prompt,
        max_new_tokens=60,
        do_sample=False,
    )

    return result[0]["generated_text"]
