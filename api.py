# api.py

from fastapi import FastAPI
from screener import analyze_stock, run_screener
from market_data import TOP_50_NSE

app = FastAPI()


@app.get("/")
def home():
    return {"message": "AI Stock API Running"}


@app.get("/stock/{symbol}")
def stock_analysis(symbol: str):
    return analyze_stock(symbol)


@app.get("/top50")
def top50():
    df = run_screener(TOP_50_NSE)
    return df.to_dict(orient="records")