import streamlit as st
from datetime import datetime, timedelta, timezone

from scraper import fetch_headlines
from scraper_url import fetch_headlines_from_url
from scorer import score_batch, weighted_average

st.set_page_config(page_title="VertexStudy", layout="wide")

# --- Modern green dashboard style ---
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

body {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 40%, #f0fdf4 100%);
}

.block-container {
    padding-top: 2rem;
}

.header {
    background: linear-gradient(135deg, #22c55e, #4ade80);
    padding: 1.5rem;
    border-radius: 16px;
    color: white;
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 25px rgba(34,197,94,0.25);
}

.card {
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(10px);
    padding: 1rem;
    border-radius: 16px;
    margin-bottom: 1rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}

.positive { color: #16a34a; font-weight: 600; }
.neutral { color: #6b7280; font-weight: 600; }
.negative { color: #dc2626; font-weight: 600; }

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">📈 VertexStudy Sentiment Dashboard</div>', unsafe_allow_html=True)

query = st.text_input("Enter ticker or URL")
run = st.button("Analyze")


def filter_by_time(items, window):
    if not window:
        return items
    now = datetime.now(timezone.utc)
    return [i for i in items if not i.published_at or now - i.published_at <= window]

if run and query:
    try:
        if query.startswith("http"):
            items = fetch_headlines_from_url(query)
        else:
            items = fetch_headlines(query)

        items = filter_by_time(items, None)
        results = score_batch([i.text for i in items])
        avg = weighted_average(results, items)

        st.markdown(f"""<div class='card'>
        <b>Overall Score:</b> {avg:.3f}
        </div>""", unsafe_allow_html=True)

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
