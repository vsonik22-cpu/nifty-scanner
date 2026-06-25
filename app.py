import streamlit as st

st.set_page_config(page_title="Nifty500 Scanner", layout="wide")

st.title("🚀 Elliott Multi-Timeframe Scanner")

st.markdown(
    "### 5m • 15m • 1H • Daily • Weekly Analysis"
)

st.write("Scanner is starting...")
import pandas as pd
import requests

@st.cache_data(ttl=3600)
def get_nifty500():
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    df = pd.read_csv(url)
    return df

nifty500 = get_nifty500()

symbols = nifty500["Symbol"].head(100).tolist()

st.metric("Stocks Scanned", len(symbols))

import yfinance as yf
def check_trend(df):
    if df.empty or len(df) < 15:
        return "SIDE"

    try:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        h = df["High"].iloc[-1]
        hp = df["High"].iloc[-2]

        l = df["Low"].iloc[-1]
        lp = df["Low"].iloc[-2]

        c = df["Close"].iloc[-1]

        sh = df["High"].tail(15).max()
        sl = df["Low"].tail(15).min()

        f618 = sh - (sh - sl) * 0.618
        f50 = sh - (sh - sl) * 0.50
        f382 = sh - (sh - sl) * 0.382

        is_up = (
            h > hp and
            l > lp and
            c > hp and
            c > f382 and
            c > f50 and
            c > f618
        )

        is_down = (
            h < hp and
            l < lp and
            c < lp and
            c < f382 and
            c < f50 and
            c < f618
        )

        if is_up:
            return "BUY"
        elif is_down:
            return "SELL"
        else:
            return "SIDE"

    except:
        return "ERROR"

results = []

for sym in symbols:
    row = {"Stock": sym}

    timeframes = {
        "5m": ("5d", "5m"),
        "15m": ("15d", "15m"),
        "1h": ("60d", "60m"),
        "Daily": ("1y", "1d"),
        "Weekly": ("5y", "1wk")
    }

    for tf, (period, interval) in timeframes.items():
        try:
            df = yf.download(
                sym + ".NS",
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=False
            )

            signal = check_trend(df)

        except Exception:
            signal = "ERROR"

        row[tf] = signal

    results.append(row)

df_result = pd.DataFrame(results)

buy_count = (
    (df_result["5m"] == "BUY") |
    (df_result["15m"] == "BUY") |
    (df_result["1h"] == "BUY")
).sum()

sell_count = (
    (df_result["5m"] == "SELL") |
    (df_result["15m"] == "SELL") |
    (df_result["1h"] == "SELL")
).sum()

col1, col2 = st.columns(2)

col1.metric("🟢 BUY Stocks", int(buy_count))
col2.metric("🔴 SELL Stocks", int(sell_count))
strong_buy = df_result[
    (df_result["5m"] == "BUY") &
    (df_result["15m"] == "BUY")
]

strong_sell = df_result[
    (df_result["5m"] == "SELL") &
    (df_result["15m"] == "SELL")
]

st.subheader("🔥 Strong BUY Stocks")
st.dataframe(strong_buy)

st.subheader("⚠️ Strong SELL Stocks")
st.dataframe(strong_sell)
st.subheader("📊 Scanner Result")
def color_signal(val):
    if val == "BUY":
        return "background-color: green; color: white"
    elif val == "SELL":
        return "background-color: red; color: white"
    else:
        return "background-color: gray; color: white"
styled_df = df_result.style.map(
    color_signal,
    subset=["5m", "15m", "1h", "Daily", "Weekly"]
)

st.dataframe(styled_df)
    
