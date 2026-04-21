from fastapi import FastAPI
from analysis_pipeline import analyze_ticker, analyze_url, parse_window

app = FastAPI()

@app.get("/analyze")
def analyze(ticker: str = None, url: str = None, window: str = None):
    try:
        w = parse_window(window) if window else None
    except Exception:
        return {"error": "Invalid window format"}

    if ticker:
        analyze_ticker(ticker, w)
        return {"message": f"Ran analysis for ticker {ticker}"}
    elif url:
        analyze_url(url, w)
        return {"message": "Ran analysis for URL"}
    else:
        return {"error": "Provide ticker or url"}
