import streamlit as st

from scraper import fetch_headlines
from scraper_url import fetch_headlines_from_url
from scorer import score_batch, weighted_average

st.set_page_config(
    page_title="Stock Sentiment Analysis - Nameera's Independent Study",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
<style>
header {
    visibility: hidden;
}

[data-testid="stToolbar"] {
    display: none;
}

[data-testid="stDecoration"] {
    display: none;
}

[data-testid="stStatusWidget"] {
    display: none;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.stApp {
    background: linear-gradient(180deg, #022c22 0%, #052e16 45%, #020617 100%);
    color: white;
}

.block-container {
    max-width: 1100px;
    padding-top: 1rem;
}

.hero {
    padding: 2rem;
    border-radius: 24px;
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.18);
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.hero-title {
    font-size: 3rem;
    font-weight: 700;
    color: #ecfdf5;
}

.hero-subtitle {
    color: #a7f3d0;
    font-size: 1.1rem;
    margin-top: 0.5rem;
}

label[data-testid="stWidgetLabel"] {
    color: white !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
}

.metric-card {
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.15);
    border-radius: 18px;
    padding: 1.25rem;
    text-align: center;
    backdrop-filter: blur(10px);
}

.metric-title {
    color: #a7f3d0;
    font-size: 0.95rem;
}

.metric-value {
    color: white;
    font-size: 2rem;
    font-weight: 700;
    margin-top: 0.5rem;
}

.sentiment-positive {
    color: #4ade80;
}

.sentiment-negative {
    color: #f87171;
}

.sentiment-neutral {
    color: #facc15;
}

.news-card {
    background: rgba(16, 185, 129, 0.06);
    border: 1px solid rgba(16, 185, 129, 0.12);
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

.source-url {
    margin-top: 0.6rem;
    font-size: 0.9rem;
}

.source-url a {
    color: #6ee7b7;
    text-decoration: none;
    font-weight: 600;
}

.source-url a:hover {
    text-decoration: underline;
}

.stTextInput input {
    border-radius: 14px;
    border: 1px solid rgba(16, 185, 129, 0.2);
    background: white;
    color: black !important;
    font-size: 1.15rem;
    font-weight: 500;
    padding: 0.9rem;
}

.stButton button {
    width: 100%;
    border-radius: 14px;
    border: none;
    background: linear-gradient(90deg, #10b981, #22c55e);
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
    <div class='hero-title'>📈 Stock Sentiment Analysis</div>
    <div class='hero-subtitle'>Nameera's Independent Study • AI-powered financial sentiment analysis using FinBERT</div>
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
    if avg >= 0.5:
        return "Strongly Positive", "sentiment-positive"
    elif avg >= 0.15:
        return "Positive", "sentiment-positive"
    elif avg <= -0.5:
        return "Strongly Negative", "sentiment-negative"
    elif avg <= -0.15:
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

        st.markdown(f"### Source: `{query}`")

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

            item_url = getattr(item, 'url', query)

            st.markdown(
                f"""
<div class='news-card'>
    <div class='news-text'>{item.text}</div>
    <div class='news-score {cls}'>
        {res.label} • Confidence {res.confidence * 100:.1f}%
    </div>
    <div class='source-url'>
        🔗 <a href='{item_url}' target='_blank'>Open Article</a>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.error(str(e))
