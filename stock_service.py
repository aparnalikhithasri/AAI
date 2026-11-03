"""
Stock Service Module for 'Reasoning Is All You Need'
Manages local stock historical data and news loading without external APIs.
"""

import os
import json
import pandas as pd
from utils.indicators import add_all_indicators

STOCK_METADATA = {
    "TCS": {
        "name": "Tata Consultancy Services Ltd.",
        "sector": "Information Technology",
        "currency": "₹",
        "description": "India's largest IT services and consulting company."
    },
    "INFY": {
        "name": "Infosys Limited",
        "sector": "Information Technology",
        "currency": "₹",
        "description": "Global leader in next-generation digital services and consulting."
    },
    "RELIANCE": {
        "name": "Reliance Industries Limited",
        "sector": "Energy & Conglomerate",
        "currency": "₹",
        "description": "Diversified conglomerate spanning petrochemicals, telecom (Jio), and retail."
    },
    "HDFCBANK": {
        "name": "HDFC Bank Limited",
        "sector": "Banking & Financial Services",
        "currency": "₹",
        "description": "India's largest private sector bank by assets and market capitalization."
    },
    "AAPL": {
        "name": "Apple Inc.",
        "sector": "Consumer Electronics & Tech",
        "currency": "$",
        "description": "Global technology company designing smartphones, hardware, and digital services."
    }
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def get_available_stocks() -> list:
    """Return list of supported stock symbols."""
    return list(STOCK_METADATA.keys())

def get_stock_info(symbol: str) -> dict:
    """Return metadata for a specific stock."""
    return STOCK_METADATA.get(symbol.upper(), {
        "name": symbol,
        "sector": "General",
        "currency": "₹",
        "description": "Educational demo stock."
    })

def load_stock_data(symbol: str, with_indicators: bool = True) -> pd.DataFrame:
    """
    Load stock historical data from local CSV file.
    Optionally computes all technical indicators (SMA20, SMA50, RSI, MACD).
    """
    symbol = symbol.upper()
    csv_path = os.path.join(DATA_DIR, "stocks", f"{symbol}.csv")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Historical stock data file not found at {csv_path}")
        
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    
    if with_indicators:
        df = add_all_indicators(df)
        
    return df

def get_latest_price(symbol: str) -> float:
    """Get the most recent closing price for a stock from local data."""
    df = load_stock_data(symbol, with_indicators=False)
    if df.empty:
        raise ValueError(f"No price data available for {symbol}")
    return float(df['Close'].iloc[-1])

def get_stock_summary(symbol: str) -> dict:
    """
    Get a summary of price, change, volume, and range for a stock.
    """
    df = load_stock_data(symbol, with_indicators=True)
    info = get_stock_info(symbol)
    
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    change = round(latest['Close'] - prev['Close'], 2)
    change_pct = round((change / prev['Close']) * 100, 2) if prev['Close'] != 0 else 0.0
    
    return {
        "symbol": symbol,
        "name": info["name"],
        "sector": info["sector"],
        "currency": info["currency"],
        "current_price": round(float(latest['Close']), 2),
        "open": round(float(latest['Open']), 2),
        "high": round(float(latest['High']), 2),
        "low": round(float(latest['Low']), 2),
        "volume": int(latest['Volume']),
        "change": change,
        "change_pct": change_pct,
        "sma_20": round(float(latest['SMA_20']), 2),
        "sma_50": round(float(latest['SMA_50']), 2),
        "rsi": round(float(latest['RSI']), 2),
        "macd": round(float(latest['MACD']), 2),
        "macd_signal": round(float(latest['MACD_Signal']), 2),
        "macd_hist": round(float(latest['MACD_Hist']), 2),
        "high_52w": round(float(df['High'].max()), 2),
        "low_52w": round(float(df['Low'].min()), 2),
        "data_points": len(df)
    }

def load_stock_news(symbol: str) -> list:
    """
    Load local news articles for a specific stock from data/news/news.json.
    """
    symbol = symbol.upper()
    json_path = os.path.join(DATA_DIR, "news", "news.json")
    
    if not os.path.exists(json_path):
        return []
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            all_news = json.load(f)
            
        stock_news = [item for item in all_news if item.get("stock", "").upper() == symbol]
        # Sort by date descending if available
        stock_news.sort(key=lambda x: x.get("date", ""), reverse=True)
        return stock_news
    except Exception as e:
        print(f"Error loading news: {e}")
        return []
