from fastapi import FastAPI
from analysis_pipeline import analyze_ticker, analyze_url, parse_window

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/analyze")
def analyze(ticker: str = None, url: str = None, window: str = None):
    try:
        w = parse_window(window) if window else None
    except Exception:
        return {"error": "Invalid window format"}

    if ticker:
        return analyze_ticker(ticker, w, output_mode="data")
    elif url:
        return analyze_url(url, w, output_mode="data")
    else:
        return {"error": "Provide ticker or url"}
