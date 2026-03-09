import yfinance as yf
import pandas as pandas
#import streamlit as st

#@st.cache_data(ttl=300)
def get_stock_data(ticker, period='30d'):

    stock = yf.Ticker(ticker)

    history = stock.history(period=period, interval='1d')

    info = stock.info

    stock_summary = {

        'ticker': ticker.upper(),
        'company_name': info.get('longName', ticker),
        'current_name': info.get('longName', ticker),
        'current_price': info.get('currentPrice', 'N/A'),
        'previous_close': info.get('previousClose', 'N/A'),
        'market_cap': info.get('marketCap', 'N/A'),
        'sector': info.get('sector', 'N/A'),
        'history': history

    }

    return stock_summary

if __name__ == "__main__":
    print("Fetching stock data for Apple (AAPL)...\n")
    data = get_stock_data("AAPL")

    print(f"Company:        {data['company_name']}")
    print(f"Ticker:         {data['ticker']}")
    print(f"Current Price:  ${data['current_price']}")
    print(f"Previous Close: ${data['previous_close']}")
    print(f"Market Cap:     ${data['market_cap']:,}")
    print(f"Sector:         {data['sector']}")
    print(f"\nLast 5 days of price history:")
    print(data['history'].tail())



