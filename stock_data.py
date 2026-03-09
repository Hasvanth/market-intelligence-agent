import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_stock_data(ticker: str) -> dict:
  
    api_key  = os.getenv("FINNHUB_API_KEY")
    base_url = "https://finnhub.io/api/v1"

    # ── Current Quote ──
    quote_url = f"{base_url}/quote?symbol={ticker}&token={api_key}"
    quote = requests.get(quote_url).json()

    current_price  = round(quote.get("c", 0), 2)   # c = current price
    previous_close = round(quote.get("pc", 0), 2)  # pc = previous close

    # ── Company Profile ──
    profile_url = f"{base_url}/stock/profile2?symbol={ticker}&token={api_key}"
    profile = requests.get(profile_url).json()

    company_name = profile.get("name", ticker)
    sector       = profile.get("finnhubIndustry", "N/A")
    market_cap   = int(profile.get("marketCapitalization", 0) * 1_000_000)

    # ── 30 Day Price History ──
    end   = int(datetime.now().timestamp())
    start = int((datetime.now() - timedelta(days=30)).timestamp())

    candle_url = f"{base_url}/stock/candle?symbol={ticker}&resolution=D&from={start}&to={end}&token={api_key}"
    candles = requests.get(candle_url).json()

    # Build DataFrame from candle data
    if candles.get("s") == "ok":
        history_df = pd.DataFrame({
            "Close":  candles["c"],
            "Volume": candles["v"]
        }, index=pd.to_datetime(candles["t"], unit="s"))
        history_df.index.name = "Date"
    else:
        history_df = pd.DataFrame(columns=["Close", "Volume"])

    return {
        "ticker":         ticker,
        "company_name":   company_name,
        "current_price":  current_price,
        "previous_close": previous_close,
        "market_cap":     market_cap,
        "sector":         sector,
        "history":        history_df
    }


if __name__ == "__main__":
    data = get_stock_data("AAPL")
    print(f"Company:       {data['company_name']}")
    print(f"Current Price: ${data['current_price']}")
    print(f"Prev Close:    ${data['previous_close']}")
    print(f"Sector:        {data['sector']}")
    print(f"Market Cap:    ${data['market_cap']:,}")
    print(f"History rows:  {len(data['history'])}")
