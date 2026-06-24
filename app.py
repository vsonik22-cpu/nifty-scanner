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
    if df.empty or len(df) < 2:
        return "SIDE"

    try:
        h = df["High"].values[-1]
        hp = df["High"].values[-2]

        l = df["Low"].values[-1]
        lp = df["Low"].values[-2]

        c = df["Close"].values[-1]
        v = df["Volume"].values[-1]

        is_up = (h > hp) and (l > lp) and (c > hp) and (v > 0)
        is_down = (h < hp) and (l < lp) and (c < lp) and (v > 0)

        if is_up:
            return "BUY"
        elif is_down:
            return "SELL"
        else:
            return "SIDE"

    except Exception as e:
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
    