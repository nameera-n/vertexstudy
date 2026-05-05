import streamlit as st

from scraper import fetch_headlines
from scraper_url import fetch_headlines_from_url
from scorer import score_batch, weighted_average

st.set_page_config(page_title="VertexStudy", page_icon="📈", layout="wide")

st.markdown(
    """
<style>
.stApp {
    background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
    color: white;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
}

.hero {
    padding: 2rem;
    border-radius: 24px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 2rem;
}

.hero-title {
    font-size: 3rem;
    font-weight: 700;
    color: white;
}

.hero-subtitle {
    color: #cbd5e1;
    font-size: 1.1rem;
    margin-top: 0.5rem;
}

.metric-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 1.25rem;
    text-align: center;
}

.metric-title {
    color: #94a3b8;
    font-size: 0.95rem;
}

.metric-value {
    color: white;
    font-size: 2rem;
    font-weight: 700;
    margin-top: 0.5rem;
}

.sentiment-positive {
    color: #22c55e;
}

.sentiment-negative {
    color: #ef4444;
}

.sentiment-neutral {
    color: #facc15;
}

.news-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.news-text {
    color: white;
    font-size: 1rem;
    line-height: 1.5;
}

.news-score {
    margin-top: 0.75rem;
    font-weight: 600;
}

.stTextInput input {
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.15);
    background: rgba(255,255,255,0.05);
    color: white;
}

.stButton button {
    width: 100%;
    border-radius: 14px;
    border: none;
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    color: white;
    font-weight: 600;
    padding: 0.75rem;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class='hero'>
    <div class='hero-title'>📈 VertexStudy</div>
    <div class='hero-subtitle'>AI-powered stock and finance sentiment dashboard using FinBERT</div>
</div>
""",
    unsafe_allow_html=True,
)

query = st.text_input(
    "Enter a stock ticker or finance article URL",
    placeholder="NVDA or https://finance.yahoo.com/...",
)

run = st.button("Analyze Sentiment")


def get_sentiment_label(avg):
    if avg > 0.1:
        return "Positive", "sentiment-positive"
    elif avg < -0.1:
        return "Negative", "sentiment-negative"
    return "Neutral", "sentiment-neutral"


if run and query:
    try:
        with st.spinner("Running FinBERT sentiment analysis..."):
            if query.startswith("http"):
                items = fetch_headlines_from_url(query)
            else:
                items = fetch_headlines(query)

            results = score_batch([i.text for i in items])
            avg = weighted_average(results, items)
            sentiment, sentiment_class = get_sentiment_label(avg)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
<div class='metric-card'>
    <div class='metric-title'>Overall Sentiment</div>
    <div class='metric-value {sentiment_class}'>{sentiment}</div>
</div>
""",
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
<div class='metric-card'>
    <div class='metric-title'>Sentiment Score</div>
    <div class='metric-value'>{avg:.3f}</div>
</div>
""",
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
<div class='metric-card'>
    <div class='metric-title'>Articles Analyzed</div>
    <div class='metric-value'>{len(results)}</div>
</div>
""",
                unsafe_allow_html=True,
            )

        st.markdown("## Latest Headlines")

        for item, res in zip(items[:10], results[:10]):
            if res.score > 0:
                cls = "sentiment-positive"
            elif res.score < 0:
                cls = "sentiment-negative"
            else:
                cls = "sentiment-neutral"

            st.markdown(
                f"""
<div class='news-card'>
    <div class='news-text'>{item.text}</div>
    <div class='news-score {cls}'>
        {res.label} • Confidence {res.confidence * 100:.1f}%
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.error(str(e))
