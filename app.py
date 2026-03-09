#import streamlit as st
#mport plotly.graph_objects as go
#import pandas as pd
#from stock_data import get_stock_data
#from sentiment import analyze_company_sentiment
#from agent import analyze_company
#import os
#os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
#os.environ["NEWS_API_KEY"] = st.secrets["NEWS_API_KEY"]
#os.environ["FINNHUB_API_KEY"] = st.secrets["FINNHUB_API_KEY"]
#os.environ["TWELVEDATA_API_KEY"] = st.secrets["TWELVEDATA_API_KEY"]

import os
import streamlit as st

# Load secrets FIRST before any other imports
try:
    os.environ["OPENAI_API_KEY"]     = st.secrets["OPENAI_API_KEY"]
    os.environ["NEWS_API_KEY"]       = st.secrets["NEWS_API_KEY"]
    os.environ["FINNHUB_API_KEY"]    = st.secrets["FINNHUB_API_KEY"]
    os.environ["TWELVEDATA_API_KEY"] = st.secrets["TWELVEDATA_API_KEY"]
except Exception:
    pass  # running locally — keys come from .env file instead

import plotly.graph_objects as go
import pandas as pd
from stock_data import get_stock_data
from sentiment import analyze_company_sentiment
from agent import analyze_company


st.set_page_config(
    page_title="AI Market Intelligence",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
    <style>
    .big-font { font-size: 28px; font-weight: bold; }
    .bullish  { color: #00C853; font-weight: bold; font-size: 20px; }
    .bearish  { color: #FF1744; font-weight: bold; font-size: 20px; }
    .neutral  { color: #9E9E9E; font-weight: bold; font-size: 20px; }
    </style>
""", unsafe_allow_html=True)



st.title("🤖 AI Market Intelligence Agent")
st.markdown("*Powered by GPT-4o-mini, LangGraph, RAG, and Sentiment Analysis*")
st.divider()

st.sidebar.title("🔍 Analyze A Stock")
st.sidebar.markdown("Enter a company to get a full AI analysis.")

company_name = st.sidebar.text_input(
    "Company Name",
    value="Apple",
    placeholder="e.g. Apple, Tesla, Microsoft"
)

ticker = st.sidebar.text_input(
    "Stock Ticker",
    value="AAPL",
    placeholder="e.g. AAPL, TSLA, MSFT"
)

analyze_button = st.sidebar.button(
    "🚀 Run Analysis",
    use_container_width=True
)

st.sidebar.divider()
st.sidebar.markdown("**How It Works:**")
st.sidebar.markdown("1. Fetches live news")
st.sidebar.markdown("2. Gets real stock price")
st.sidebar.markdown("3. Runs sentiment analysis")
st.sidebar.markdown("4. AI agent generates report")


# --MAIN DASHBOARD --

if analyze_button:

    # ── STOCK DATA ──
    with st.spinner(f"Fetching stock data for {ticker}..."):
        try:
            stock = get_stock_data(ticker)
        except Exception as e:
            st.error(f"Could not fetch stock data: {e}")
            st.stop()

    # ── TOP METRICS ROW ──
    st.subheader(f"📊 {stock['company_name']} ({stock['ticker']})")

    col1, col2, col3, col4 = st.columns(4)

    price_change = stock['current_price'] - stock['previous_close']
    #price_change_pct = (price_change / stock['previous_close']) * 100

    if stock['previous_close'] and stock['previous_close'] != 0:
        price_change_pct = (price_change / stock['previous_close']) * 100
    else:
        price_change_pct = 0

    with col1:
        st.metric(
            label="Current Price",
            value=f"${stock['current_price']}",
            delta=f"{price_change_pct:.2f}%"
        )
    with col2:
        st.metric(
            label="Previous Close",
            value=f"${stock['previous_close']}"
        )
    with col3:
        st.metric(
            label="Sector",
            value=stock['sector']
        )
    with col4:
        market_cap = stock.get('market_cap', 0)
        if market_cap:
            market_cap_str = f"${market_cap/1e9:.1f}B"
        else:
            market_cap_str = "N/A"
        st.metric(
            label="Market Cap",
            value=market_cap_str
        )

    st.divider()

    # ── STOCK PRICE CHART ──
    st.subheader("📈 Price History")

    history = stock['history']
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=history.index,
        y=history['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color='#1B4FDB', width=2)
    ))

    fig.add_trace(go.Bar(
        x=history.index,
        y=history['Volume'],
        name='Volume',
        yaxis='y2',
        opacity=0.3,
        marker_color='#90CAF9'
    ))

    fig.update_layout(
        title=f"{stock['company_name']} — Last 30 Days",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        yaxis2=dict(
            title="Volume",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        hovermode='x unified',
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    # ── SENTIMENT ANALYSIS ──
    st.subheader("🧠 News Sentiment Analysis")

    with st.spinner("Analyzing news sentiment..."):
        sentiment_data = analyze_company_sentiment(company_name)

    score = sentiment_data['overall_score']
    signal = sentiment_data['overall_signal']

    scol1, scol2, scol3 = st.columns(3)
    with scol1:
        st.metric('Overall Score', f'{score:.3f}')
    with scol2:
        st.metric('Overall Signal', signal)
    with scol3:
        st.metric('Articles Analyzed', sentiment_data['total_articles'])

    # Sentiment gauge chart
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': 'Sentiment Score'},
        gauge={
            'axis': {'range': [-1, 1]},
            'bar': {'color': '#1B4FDB'},
            'steps': [
                {'range': [-1, -0.05], 'color': '#FFCDD2'},
                {'range': [-0.05, 0.05], 'color': '#F5F5F5'},
                {'range': [0.05, 1], 'color': '#C8E6C9'}
            ],
            'threshold': {
                'line': {'color': 'black', 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    gauge.update_layout(height=300)
    st.plotly_chart(gauge, use_container_width=True)

    # Individual articles
    st.markdown("**Individual Article Scores:**")
    for article in sentiment_data['articles']:
        if article['signal'] == 'BULLISH':
            color = "🟢"
        elif article['signal'] == 'BEARISH':
            color = "🔴"
        else:
            color = "⚪"
        with st.expander(f"{color} {article['signal']} | Score: {article['score']:.3f} | {article['title'][:80]}"):
            st.write(f"**Source:** {article['source']}")
            st.write(f"**Date:** {article['date']}")
            st.write(f"**Score:** {article['score']}")
            st.write(f"**Signal:** {article['signal']}")

    st.divider()

    # ── AI AGENT REPORT ──
    st.subheader("🤖 AI Agent Full Analysis")

    with st.spinner("AI Agent is analyzing... this may take 30-60 seconds..."):
        try:
            report = analyze_company(company_name, ticker)
        except Exception as e:
            st.error(f"Agent error: {e}")
            report = None

    if report:
        if 'BUY' in report.upper():
            signal_color = "bullish"
            signal_text = "🟢 BUY"
        elif 'SELL' in report.upper():
            signal_color = "bearish"
            signal_text = "🔴 SELL"
        else:
            signal_color = "neutral"
            signal_text = "⚪ HOLD"

        st.markdown(f'<p class="{signal_color}">Signal: {signal_text}</p>',
                    unsafe_allow_html=True)
        st.markdown('---')
        st.markdown(report)

else:
    st.markdown('### 👈 Enter a company name and ticker in the sidebar, then click Run Analysis')
    st.markdown('')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info('📰 **Live News**\nFetches latest news from NewsAPI')
    with col2:
        st.info('📈 **Stock Data**\nReal prices from Yahoo Finance')
    with col3:
        st.info('🤖 **AI Analysis**\nGPT-4o-mini generates BUY/SELL/HOLD')

