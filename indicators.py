"""
Technical Indicators Module for 'Reasoning Is All You Need'
Calculates Moving Averages (SMA20, SMA50), RSI (14), and MACD (12, 26, 9)
Pure Python & Pandas implementations suitable for educational demonstrations.
"""

import pandas as pd
import numpy as np

def calculate_sma(series: pd.Series, window: int) -> pd.Series:
    """Calculate Simple Moving Average."""
    return series.rolling(window=window, min_periods=1).mean()

def calculate_ema(series: pd.Series, span: int) -> pd.Series:
    """Calculate Exponential Moving Average."""
    return series.ewm(span=span, adjust=False).mean()

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    Formula: RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss over the period.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Calculate exponential moving average of gains and losses
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    
    # Fill initial NaN values gracefully with neutral 50
    return rsi.fillna(50.0).round(2)

def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """
    Calculate MACD (Moving Average Convergence Divergence).
    Returns (macd_line, signal_line, histogram)
    """
    fast_ema = calculate_ema(series, fast)
    slow_ema = calculate_ema(series, slow)
    macd_line = fast_ema - slow_ema
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    
    return macd_line.round(2), signal_line.round(2), histogram.round(2)

def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a stock dataframe with 'Close' column and adds all technical indicators:
    - SMA_20
    - SMA_50
    - RSI
    - MACD
    - MACD_Signal
    - MACD_Hist
    """
    df = df.copy()
    if 'Close' not in df.columns:
        raise ValueError("DataFrame must contain a 'Close' column")
        
    df['SMA_20'] = calculate_sma(df['Close'], 20).round(2)
    df['SMA_50'] = calculate_sma(df['Close'], 50).round(2)
    df['RSI'] = calculate_rsi(df['Close'], 14)
    macd, signal, hist = calculate_macd(df['Close'], 12, 26, 9)
    df['MACD'] = macd
    df['MACD_Signal'] = signal
    df['MACD_Hist'] = hist
    
    return df
