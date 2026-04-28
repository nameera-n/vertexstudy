import streamlit as st
from datetime import datetime, timezone

from scraper import fetch_headlines
from scraper_url import fetch_headlines_from_url
from scorer import score_batch, weighted_average

st.set_page_config(page_title="VertexStudy", layout="wide")

# --- Clean modern dashboard UI ---
st.markdown("""
<style>
body {
    background: #f8fafc;
}
.block-container {
    max-width: 900px;
    padding-top: 2rem;
}
.header {
    font-size: 1.6rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: #111827;
}
.stButton button {
    border-radius: 10px;
    background: #16a34a;
    color: white;
    border: none;
}
.card {
    background: white;
    padding: 1rem;
    border-radius: 14px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
.positive { color: #16a34a; font-weight: 600; }
.neutral { color: #6b7280; font-weight: 600; }
.negative { color: #dc2626; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">VertexStudy — Sentiment Analysis</div>', unsafe_allow_html=True)

query = st.text_input("Enter ticker or URL")
run = st.button("Analyze")


def get_sentiment_label(avg):
    if avg > 0.1:
        return "Positive"
    elif avg < -0.1:
        return "Negative"
    return "Neutral"


if run and query:
    try:
        with st.spinner("Analyzing with FinBERT..."):
            if query.startswith("http"):
                items = fetch_headlines_from_url(query)
            else:
                items = fetch_headlines(query)

            results = score_batch([i.text for i in items])
            avg = weighted_average(results, items)
            sentiment = get_sentiment_label(avg)

        st.markdown(f"""
        <div class='card'>
        <b>Overall Sentiment:</b> {sentiment}<br>
        <b>Score:</b> {avg:.3f}<br>
        <b>Items:</b> {len(results)}
        </div>
        """, unsafe_allow_html=True)

        for item, res in zip(items[:10], results[:10]):
            cls = "positive" if res.score > 0 else "negative" if res.score < 0 else "neutral"
            st.markdown(f"""
            <div class='card'>
                {item.text}<br>
                <span class='{cls}'>{res.label} ({res.confidence*100:.1f}%)</span>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(str(e))
