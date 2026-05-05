# VertexStudy

Simple sentiment analysis pipeline for stock tickers and finance article URLs.

## 1) Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) CLI usage

```bash
python3 main.py TickerNameHere
python3 main.py https://www.urlofarticle.com/article
python3 main.py ORCL MSFT NVDA META
```

Examples:

```bash
python3 main.py ORCL
python3 main.py https://finance.yahoo.com/news/oracle-plans-thousands-job-cuts-180243222.html
```

## 3) API usage (FastAPI)

Run the API:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Analyze ticker:

```bash
curl "http://localhost:8000/analyze?ticker=NVDA"
```

Analyze URL:

```bash
curl "http://localhost:8000/analyze?url=https://finance.yahoo.com/news/oracle-plans-thousands-job-cuts-180243222.html"
```

## 4) Streamlit UI (optional)

```bash
streamlit run ui.py
```
