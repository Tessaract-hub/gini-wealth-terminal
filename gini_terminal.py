import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

st.set_page_config(page_title="GINI Wealth Terminal", layout="wide", page_icon="💎")
st.markdown("""
<style>
    /* Whole app background */
    .stApp {
        background-color: #0A0A0A;
        color: #00FFE0;
    }

    /* Titles and text */
    h1, h2, h3, h4, h5, h6, p {
        color: #D800FF !important;
    }

    /* Metrics boxes */
    div[data-testid="stMetric"] {
        background-color: #1a1a1a;
        border: 2px solid #D800FF;
        border-radius: 12px;
        padding: 10px;
        margin: 5px;
        color: #00FFE0 !important;
    }

    /* Buttons */
    button, .stButton>button {
        background: linear-gradient(90deg, #D800FF, #00FFE0);
        color: #0A0A0A;
        border: none;
        border-radius: 8px;
    }

    /* PDF button override */
    div.stDownloadButton button {
        background: linear-gradient(90deg, #FF00AA, #00FFE0);
        color: #0A0A0A;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0A0A0A;
    }
</style>
""", unsafe_allow_html=True)
st.title("💎 GINI Wealth Terminal")
st.markdown("#### Compare multiple assets & download your cosmic report as PDF 🚀")

tickers_input = st.sidebar.text_input("Enter Stock or Crypto Tickers (comma separated)", value="AAPL, TSLA, BTC-USD")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2023-01-01"))

def fetch_prices(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data['Close'].dropna()

def calculate_gini(x):
    sorted_x = np.sort(x)
    n = len(sorted_x)
    cumulative = np.cumsum(sorted_x)
    return (n + 1 - 2 * np.sum(cumulative) / cumulative[-1]) / n

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
gini_scores = {}

fig, ax = plt.subplots(figsize=(10, 7))
ax.set_facecolor("#0A0A0A")
fig.patch.set_facecolor('#0A0A0A')
ax.spines[:].set_color('white')
ax.tick_params(colors='white')
colors = ["#D800FF", "#00FFE0", "#FF0080", "#FFAA00", "#00FF44"]

for idx, ticker in enumerate(tickers):
    prices = fetch_prices(ticker, start_date, end_date)
    if len(prices) == 0:
        st.warning(f"⛔ {ticker}: No price data found. Skipping.")
        continue

    gini = calculate_gini(prices)
    gini_scores[ticker] = gini
    st.metric(f"{ticker} GINI Coefficient", f"{gini:.3f}")

    sorted_prices = np.sort(prices)
    cumulative_prices = np.cumsum(sorted_prices) / np.sum(sorted_prices)
    lorenz_x = np.insert(np.linspace(0, 1, len(cumulative_prices)), 0, 0)
    lorenz_y = np.insert(cumulative_prices, 0, 0)

    ax.plot(lorenz_x, lorenz_y, color=colors[idx % len(colors)], linewidth=2, label=f"{ticker}")

ax.plot([0,1], [0,1], '--', color='gray')
ax.legend()
st.pyplot(fig)

# ================= PDF DOWNLOAD SECTION =================
if st.button("📄 Download PDF Report"):
    with PdfPages("GINI_Wealth_Report.pdf") as pdf:
        fig_summary, ax_sum = plt.subplots(figsize=(8,4))
        ax_sum.axis('off')
        summary_text = "\n".join([f"{t}: GINI = {g:.3f}" for t, g in gini_scores.items()])
        ax_sum.text(0.1, 0.5, "GINI Wealth Terminal Report\n\n" + summary_text, fontsize=12, color="white")
        fig_summary.patch.set_facecolor('#0A0A0A')
        pdf.savefig(fig_summary, facecolor=fig_summary.get_facecolor())
        pdf.savefig(fig)

    with open("GINI_Wealth_Report.pdf", "rb") as f:
        st.download_button("⬇️ Download GINI_Wealth_Report.pdf", f, "GINI_Wealth_Report.pdf")
