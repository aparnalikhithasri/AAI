import sys
import os

# Ensure project root is on sys.path for direct script execution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from typing import Dict, Any
from services.stock_service import load_stock_data, get_stock_info

class MarketAgent:
    """
    Agent 1: Market Analysis Agent
    Responsible for reading local stock data, calculating indicators,
    and classifying the technical market trend (BULLISH, BEARISH, NEUTRAL).
    """

    def __init__(self):
        self.name = "Market Analysis Agent"

    def analyze(self, symbol: str) -> Dict[str, Any]:
        """
        Run quantitative technical analysis on historical stock data.
        All calculations are computed mathematically in Python.
        """
        symbol = symbol.upper()
        df = load_stock_data(symbol, with_indicators=True)
        info = get_stock_info(symbol)
        
        if df.empty:
            raise ValueError(f"No price data found for {symbol}")
            
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        current_price = round(float(latest['Close']), 2)
        open_price = round(float(latest['Open']), 2)
        sma_20 = round(float(latest['SMA_20']), 2)
        sma_50 = round(float(latest['SMA_50']), 2)
        rsi = round(float(latest['RSI']), 2)
        macd = round(float(latest['MACD']), 2)
        macd_signal = round(float(latest['MACD_Signal']), 2)
        macd_hist = round(float(latest['MACD_Hist']), 2)
        
        # Trend Evaluation Scoring System
        bullish_points = 0
        bearish_points = 0
        signals = []
        
        # 1. Moving Average Alignment
        if current_price > sma_20:
            bullish_points += 1
            signals.append(f"Price ({info['currency']}{current_price}) is above 20-day MA ({info['currency']}{sma_20}).")
        else:
            bearish_points += 1
            signals.append(f"Price ({info['currency']}{current_price}) is below 20-day MA ({info['currency']}{sma_20}).")
            
        if sma_20 > sma_50:
            bullish_points += 1
            signals.append(f"20-day MA ({info['currency']}{sma_20}) is above 50-day MA ({info['currency']}{sma_50}) (Golden crossover zone).")
        else:
            bearish_points += 1
            signals.append(f"20-day MA ({info['currency']}{sma_20}) is below 50-day MA ({info['currency']}{sma_50}) (Death crossover zone).")
            
        # 2. RSI Evaluation
        if rsi > 70:
            signals.append(f"RSI is {rsi:.1f} (Overbought territory - possible near-term pullback).")
            bearish_points += 0.5
        elif rsi < 30:
            signals.append(f"RSI is {rsi:.1f} (Oversold territory - potential rebound opportunity).")
            bullish_points += 0.5
        elif rsi >= 50:
            bullish_points += 1
            signals.append(f"RSI is {rsi:.1f} (Healthy positive momentum).")
        else:
            bearish_points += 1
            signals.append(f"RSI is {rsi:.1f} (Weak or negative momentum).")
            
        # 3. MACD Evaluation
        if macd > macd_signal:
            bullish_points += 1
            signals.append(f"MACD line ({macd:.2f}) is above signal line ({macd_signal:.2f}) (Positive divergence).")
        else:
            bearish_points += 1
            signals.append(f"MACD line ({macd:.2f}) is below signal line ({macd_signal:.2f}) (Negative divergence).")
            
        # Determine overall trend
        net_score = bullish_points - bearish_points
        if net_score >= 1.5:
            trend = "BULLISH"
        elif net_score <= -1.5:
            trend = "BEARISH"
        else:
            trend = "NEUTRAL"
            
        summary_text = (
            f"{symbol} Market Analysis\n"
            f"Current Price: {info['currency']}{current_price}\n"
            f"20-Day MA: {info['currency']}{sma_20}\n"
            f"50-Day MA: {info['currency']}{sma_50}\n"
            f"RSI (14): {rsi:.1f}\n"
            f"MACD: {'Positive' if macd > macd_signal else 'Negative'} (Line: {macd:.2f}, Signal: {macd_signal:.2f})\n"
            f"Trend: {trend}"
        )
        
        return {
            "symbol": symbol,
            "name": info["name"],
            "currency": info["currency"],
            "current_price": current_price,
            "open_price": open_price,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "macd_hist": macd_hist,
            "trend": trend,
            "bullish_points": bullish_points,
            "bearish_points": bearish_points,
            "signals": signals,
            "summary_text": summary_text
        }

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    agent = MarketAgent()
    target = sys.argv[1] if len(sys.argv) > 1 else "TCS"
    print(f"=== Running Market Technical Analysis on {target} ===")
    res = agent.analyze(target)
    print(f"Current Price: {res['currency']}{res['current_price']:,.2f}")
    print(f"Trend: {res['trend']}")
    print(f"RSI (14): {res['rsi']} | 20-MA: {res['sma_20']} | 50-MA: {res['sma_50']}")
    print("Signals:")
    for s in res['signals']:
        print(f"  - {s}")


