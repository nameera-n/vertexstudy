from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from analysis_pipeline import analyze_ticker, analyze_url, parse_window

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    if url:
        return analyze_url(url, w, output_mode="data")
    return {"error": "Provide ticker or url"}
