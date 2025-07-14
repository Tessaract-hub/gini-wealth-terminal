
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="GINI Wealth Terminal", layout="wide", page_icon="💎")
st.title("💎 GINI Wealth Terminal")
st.markdown("#### Visualize your wealth distribution with cosmic precision 🌌")

ticker = st.sidebar.text_input("Enter Stock or Crypto Ticker", value="AAPL")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2023-01-01"))

def fetch_prices(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data['Close'].dropna()

prices = fetch_prices(ticker, start_date, end_date)

def calculate_gini(x):
    sorted_x = np.sort(x)
    n = len(sorted_x)
    cumulative = np.cumsum(sorted_x)
    return (n + 1 - 2 * np.sum(cumulative) / cumulative[-1]) / n

if len(prices) > 0:
    gini = calculate_gini(prices)
    st.metric("GINI Coefficient", f"{gini:.3f}")

    sorted_prices = np.sort(prices)
    cumulative_prices = np.cumsum(sorted_prices) / np.sum(sorted_prices)
    lorenz_x = np.linspace(0, 1, len(cumulative_prices))
    lorenz_y = np.insert(cumulative_prices, 0, 0)

    fig, ax = plt.subplots(figsize=(8,6))
    ax.plot(lorenz_x, lorenz_y, color="#D800FF", linewidth=2, label=f"{ticker} Lorenz Curve")
    ax.plot([0,1], [0,1], '--', color='gray')
    ax.set_facecolor("#0A0A0A")
    fig.patch.set_facecolor('#0A0A0A')
    ax.spines[:].set_color('white')
    ax.tick_params(colors='white')
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("No price data found. Try another ticker or date range.")
