from transformers import pipeline

_summarizer = None


def get_summarizer():
    global _summarizer

    if _summarizer is None:
        _summarizer = pipeline(
            "text-generation",
            model="distilgpt2"
        )

    return _summarizer


def summarize_headlines(items, max_items=10):
    texts = [item.text for item in items[:max_items] if item.text]

    if not texts:
        return "No headlines available."

    combined = ". ".join(texts)

    prompt = (
        "Financial market summary based on these headlines: "
        + combined
        + "\nSummary:"
    )

    summarizer = get_summarizer()

    result = summarizer(
        prompt,
        max_new_tokens=40,
        do_sample=False,
        truncation=True,
    )

    generated = result[0]["generated_text"]

    if "Summary:" in generated:
        generated = generated.split("Summary:")[-1].strip()

    return generated
