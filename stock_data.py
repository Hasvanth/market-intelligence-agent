
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def get_stock_data(ticker: str) -> dict:
    """
    Fetches stock data using Finnhub + Twelve Data.
    Input: stock ticker like 'AAPL', 'TSLA', 'MSFT'
    """
    ticker         = ticker.upper()
    finnhub_key    = os.getenv("FINNHUB_API_KEY")
    twelvedata_key = os.getenv("TWELVEDATA_API_KEY")

    # ────────────────────────────
    # FINNHUB — Price + Company
    # ────────────────────────────

    # Current Quote
    quote_url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={finnhub_key}"
    quote = requests.get(quote_url).json()

    current_price  = round(quote.get('c', 0), 2)
    previous_close = round(quote.get('pc', 0), 2)

    # If market closed or returns 0, use previous close
    if current_price == 0:
        current_price = previous_close

    # Company Profile
    profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={finnhub_key}"
    profile = requests.get(profile_url).json()

    company_name = profile.get('name', ticker)
    sector       = profile.get('finnhubIndustry', 'N/A')
    market_cap   = int(profile.get('marketCapitalization', 0) * 1_000_000)

    # ────────────────────────────
    # TWELVE DATA — Candle History
    # ────────────────────────────

    history_url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval=1day&outputsize=30&apikey={twelvedata_key}"
    history_response = requests.get(history_url).json()
    history_values   = history_response.get('values', [])

    if history_values:
        history_df = pd.DataFrame(history_values)
        history_df['datetime'] = pd.to_datetime(history_df['datetime'])
        history_df = history_df.set_index('datetime').sort_index()
        history_df = history_df.rename(columns={'close': 'Close', 'volume': 'Volume'})
        history_df['Close']  = history_df['Close'].astype(float)
        history_df['Volume'] = pd.to_numeric(history_df['Volume'], errors='coerce').fillna(0)
        history_df.index.name = 'Date'
    else:
        history_df = pd.DataFrame(columns=['Close', 'Volume'])

    return {
        'ticker':         ticker,
        'company_name':   company_name,
        'current_price':  current_price,
        'previous_close': previous_close,
        'market_cap':     market_cap,
        'sector':         sector,
        'history':        history_df
    }


if __name__ == "__main__":
    data = get_stock_data("AAPL")
    print(f"Company:       {data['company_name']}")
    print(f"Current Price: ${data['current_price']}")
    print(f"Prev Close:    ${data['previous_close']}")
    print(f"Sector:        {data['sector']}")
    print(f"Market Cap:    ${data['market_cap']:,}")
    print(f"History rows:  {len(data['history'])}")
    print(data['history'].tail())
