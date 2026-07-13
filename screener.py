import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# RSI CALCULATION
# ==========================================

def calculate_rsi(data, period=14):

    delta = data.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

# ==========================================
# SCORE ENGINE
# ==========================================

def calculate_score(pe_ratio, rsi, market_cap):

    score = 50

    # PE Ratio
    if pe_ratio and pe_ratio < 20:
        score += 20
    elif pe_ratio and pe_ratio < 30:
        score += 10

    # RSI
    if rsi < 30:
        score += 20
    elif rsi < 45:
        score += 10

    # Market Cap
    if market_cap and market_cap > 500_000_000_000:
        score += 10

    return min(score, 100)

# ==========================================
# RECOMMENDATION
# ==========================================

def get_recommendation(score):

    if score >= 85:
        return "🔥 Strong Buy"
    elif score >= 70:
        return "✅ Buy"
    elif score >= 55:
        return "⚠ Hold"
    else:
        return "❌ Avoid"

# ==========================================
# SINGLE STOCK ANALYSIS
# ==========================================

def analyze_stock(symbol):

    try:

        stock = yf.Ticker(symbol)
        try:
            info = stock.info
        except Exception:
            info = {}

        try:
            history = stock.history(period="6mo")
        except Exception:
            return None

        if history.empty:
            return None

        # RSI
        history["RSI"] = calculate_rsi(history["Close"])
        latest_rsi = history["RSI"].iloc[-1]

        # Fundamentals
        pe_ratio = info.get("trailingPE")
        market_cap = info.get("marketCap")
        current_price = info.get("currentPrice")

        # Score
        score = calculate_score(pe_ratio, latest_rsi, market_cap)

        recommendation = get_recommendation(score)

        return {
            "Stock": symbol,
            "Price": round(current_price, 2) if current_price else None,
            "PE Ratio": round(pe_ratio, 2) if pe_ratio else None,
            "RSI": round(latest_rsi, 2),
            "Score": score,
            "Recommendation": recommendation
        }

    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

# ==========================================
# TOP 50 SCREENER (MULTI STOCK)
# ==========================================

def run_screener(stock_list):

    results = []

    def worker(symbol):
        return analyze_stock(symbol)

    with ThreadPoolExecutor(max_workers=3) as executor:
        data = executor.map(worker, stock_list)

    for result in data:
        if result:
            results.append(result)

    df = pd.DataFrame(results)

    if not df.empty:
        df = df.sort_values(by="Score", ascending=False)

    return df