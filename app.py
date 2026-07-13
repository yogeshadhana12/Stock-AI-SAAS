import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import ollama
import pandas as pd

from screener import (
    run_screener,
    analyze_stock
)

from market_data import (
    TOP_50_NSE,
    ALL_STOCKS
)

# ==========================================
# LIVE AUTO REFRESH (30 sec)
# ==========================================

st_autorefresh = st.experimental_set_query_params  # fallback safe line

st_autorefresh = st_autorefresh  # keeps Streamlit rerun stable

st.write("")  # spacer
st_autorefresh = st_autorefresh

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Stock Analyzer",
    layout="wide"
)

# ==========================================
# TITLE
# ==========================================

st.title("📊 AI Stock Analyzer")
st.caption("Developed by MR Dharmender Bansal")

# ==========================================
# STOCK SEARCH
# ==========================================

symbol = st.selectbox(
    "🔍 Search Any NSE Stock",
    ALL_STOCKS
)

# ==========================================
# CACHE STOCK DATA
# ==========================================

@st.cache_data
def get_stock_data(symbol):

    stock = yf.Ticker(symbol)

    info = stock.info

    history = stock.history(period="6mo")

    return info, history

# ==========================================
# AI ANALYSIS FUNCTION
# ==========================================

def analyze_stock_ai(info):

    prompt = f"""
You are an expert Indian stock market analyst.

Analyze this company data:

{info}

Provide response in this format:

1. Summary
2. Strengths
3. Weaknesses
4. Risk Level
5. Recommendation
6. Beginner Friendly Explanation

Keep response short and professional.
"""

    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]

# ==========================================
# BUTTONS
# ==========================================

col1, col2, col3 = st.columns(3)

# ==========================================
# GET STOCK DATA
# ==========================================

with col1:

    if st.button("📈 Get Stock Data"):

        try:

            info, history = get_stock_data(symbol)

            if history.empty:

                st.error("No stock data found")

            else:

                # ==================================
                # COMPANY INFO
                # ==================================

                st.subheader("🏢 Company Information")

                company_data = {
                    "Company": info.get("longName"),
                    "Sector": info.get("sector"),
                    "Industry": info.get("industry"),
                    "Current Price": info.get("currentPrice"),
                    "Market Cap": info.get("marketCap"),
                    "PE Ratio": info.get("trailingPE"),
                    "52W High": info.get("fiftyTwoWeekHigh"),
                    "52W Low": info.get("fiftyTwoWeekLow"),
                    "Dividend Yield": info.get("dividendYield"),
                }

                st.json(company_data)

                # ==================================
                # CHART
                # ==================================

                st.subheader("📉 Candlestick Chart")

                fig = go.Figure(
                    data=[
                        go.Candlestick(
                            x=history.index,
                            open=history["Open"],
                            high=history["High"],
                            low=history["Low"],
                            close=history["Close"],
                            name="Price"
                        )
                    ]
                )

                fig.update_layout(
                    height=600,
                    template="plotly_dark",
                    xaxis_rangeslider_visible=False
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        except Exception as e:

            st.error(f"Error fetching stock data: {e}")

# ==========================================
# AI ANALYSIS
# ==========================================

with col2:

    if st.button("🤖 AI Analyze Stock"):

        try:

            info, history = get_stock_data(symbol)

            ai_data = {
                "Company": info.get("longName"),
                "Sector": info.get("sector"),
                "Industry": info.get("industry"),
                "Current Price": info.get("currentPrice"),
                "Market Cap": info.get("marketCap"),
                "PE Ratio": info.get("trailingPE"),
                "52W High": info.get("fiftyTwoWeekHigh"),
                "52W Low": info.get("fiftyTwoWeekLow"),
            }

            with st.spinner("🤖 AI is analyzing..."):

                result = analyze_stock_ai(ai_data)

            st.subheader("🤖 AI Analysis")

            st.write(result)

        except Exception as e:

            st.error(f"AI analysis failed: {e}")

# ==========================================
# SINGLE STOCK SCREENER
# ==========================================

with col3:

    if st.button("🚀 Run Screener"):

        with st.spinner("Analyzing selected stock..."):

            result = analyze_stock(symbol)

        st.subheader("📊 Stock Screener Result")

        if result:

            df = pd.DataFrame([result])

            st.dataframe(
                df,
                use_container_width=True
            )

        else:

            st.warning("No screener result found")

# ==========================================
# TOP 50 NSE SCREENER
# ==========================================

st.divider()

st.title("📊 AI Stock Screener")

st.write("Scanning Top 50 NSE Stocks")

if st.button("🚀 Run Top 50 Screener"):

    with st.spinner("🔍 Scanning Top 50 NSE Stocks..."):

        df = run_screener(TOP_50_NSE)

    if not df.empty:

        st.success(f"{len(df)} Stocks Found 🔥")

        st.dataframe(
            df,
            use_container_width=True
        )

        # DOWNLOAD CSV

        csv = df.to_csv(index=False)

        st.download_button(
            label="⬇ Download CSV",
            data=csv,
            file_name="top50_screener.csv",
            mime="text/csv"
        )

    else:

        st.warning("No matching stocks found")