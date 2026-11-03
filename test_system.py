"""
Verification Test Script for 'Reasoning Is All You Need'
Runs comprehensive automated unit tests across all agents, database, indicators, and services.
"""

import sys
import os

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE: Reasoning Is All You Need")
    print("==================================================")
    
    # 1. Test Indicators
    print("\n[1/7] Testing Technical Indicators...")
    from utils.indicators import calculate_sma, calculate_rsi, calculate_macd, add_all_indicators
    import pandas as pd
    import numpy as np
    
    df_sample = pd.DataFrame({
        "Date": pd.date_range("2026-01-01", periods=60),
        "Close": [100.0 + float(i) + float((i % 5) * 2) for i in range(60)]
    })
    df_ind = add_all_indicators(df_sample)
    assert "SMA_20" in df_ind.columns, "SMA_20 missing"
    assert "SMA_50" in df_ind.columns, "SMA_50 missing"
    assert "RSI" in df_ind.columns, "RSI missing"
    assert "MACD" in df_ind.columns, "MACD missing"
    print("[PASS] Indicators successfully computed.")
    
    # 2. Test Stock Service & Local Data
    print("\n[2/7] Testing Stock Service & Datasets...")
    from services.stock_service import get_available_stocks, load_stock_data, get_stock_summary, load_stock_news
    stocks = get_available_stocks()
    assert len(stocks) == 5, f"Expected 5 stocks, found {len(stocks)}"
    for s in stocks:
        df_stock = load_stock_data(s)
        assert len(df_stock) >= 100, f"{s} has fewer than 100 rows"
        summary = get_stock_summary(s)
        assert summary["current_price"] > 0, f"{s} current price invalid"
        news = load_stock_news(s)
        assert len(news) >= 5, f"{s} has fewer than 5 news items"
    print(f"[PASS] All 5 stocks (TCS, INFY, RELIANCE, HDFCBANK, AAPL) verified with 100+ rows and rich news.")

    # 3. Test SQLite Database & Paper Trading
    print("\n[3/7] Testing SQLite Paper Trading Engine...")
    from database.database import (
        init_db, get_cash_balance, execute_buy, execute_sell,
        get_holdings, get_transactions, get_portfolio_summary, reset_portfolio
    )
    reset_portfolio(1000000.0)
    assert get_cash_balance() == 1000000.0, "Initial cash balance mismatch"
    
    # Test BUY
    ok, msg, res = execute_buy("TCS", 10, 3900.0)
    assert ok, f"BUY failed: {msg}"
    assert get_cash_balance() == 961000.0, "Cash deduction failed"
    holdings = get_holdings()
    assert len(holdings) == 1 and holdings[0]["quantity"] == 10, "Holdings update failed"
    
    # Test Insufficient Cash Prevention
    ok, msg, _ = execute_buy("RELIANCE", 10000, 2800.0)
    assert not ok, "Insufficient cash check failed to reject trade"
    
    # Test SELL
    ok, msg, res = execute_sell("TCS", 5, 4000.0)
    assert ok, f"SELL failed: {msg}"
    assert get_cash_balance() == 981000.0, "Cash addition after sell failed"
    holdings = get_holdings()
    assert holdings[0]["quantity"] == 5, "Holdings post-sell mismatch"
    
    # Test Insufficient Shares Prevention
    ok, msg, _ = execute_sell("TCS", 50, 4000.0)
    assert not ok, "Insufficient shares check failed to reject sell"
    
    # Test Portfolio Summary
    port_sum = get_portfolio_summary({"TCS": 4100.0})
    assert port_sum["portfolio_value"] == 981000.0 + (5 * 4100.0), "Portfolio summary math mismatch"
    print("[PASS] Paper trading Buy/Sell/Portfolio math verified 100% accurate.")
    
    # 4. Test Market Agent
    print("\n[4/7] Testing Market Agent...")
    from agents.market_agent import MarketAgent
    m_agent = MarketAgent()
    for s in stocks:
        m_res = m_agent.analyze(s)
        assert m_res["trend"] in ["BULLISH", "BEARISH", "NEUTRAL"], f"Invalid trend {m_res['trend']}"
        assert m_res["rsi"] > 0, "Invalid RSI"
    print("[PASS] Market Agent verified across all 5 assets.")

    # 5. Test News Agent
    print("\n[5/7] Testing News Agent...")
    from agents.news_agent import NewsAgent
    n_agent = NewsAgent()
    for s in stocks:
        n_res = n_agent.analyze(s)
        assert n_res["sentiment"] in ["POSITIVE", "NEUTRAL", "NEGATIVE"], f"Invalid sentiment {n_res['sentiment']}"
        assert len(n_res["important_factors"]) > 0, "No factors found"
    print("[PASS] News Agent verified across all 5 assets.")

    # 6. Test Risk Agent
    print("\n[6/7] Testing Risk Agent...")
    from agents.risk_agent import RiskAgent
    r_agent = RiskAgent()
    for s in stocks:
        r_res = r_agent.analyze(s, proposed_quantity=15)
        assert r_res["risk_level"] in ["LOW", "MEDIUM", "HIGH"], f"Invalid risk level {r_res['risk_level']}"
        assert len(r_res["reasons"]) > 0, "No risk reasons provided"
    print("[PASS] Risk Agent verified across all 5 assets.")

    # 7. Test Decision Agent
    print("\n[7/7] Testing Decision Agent (End-to-End Synthesis)...")
    from agents.decision_agent import DecisionAgent
    d_agent = DecisionAgent()
    for s in stocks:
        m_data = m_agent.analyze(s)
        n_data = n_agent.analyze(s)
        r_data = r_agent.analyze(s, proposed_quantity=10)
        d_res = d_agent.decide(s, m_data, n_data, r_data)
        assert d_res["recommendation"] in ["BUY", "HOLD", "SELL"], f"Invalid recommendation {d_res['recommendation']}"
        assert 0 <= d_res["confidence"] <= 100, "Confidence out of bounds"
        assert len(d_res["reasons"]) >= 2, "Insufficient reasoning points"
        print(f"  -> {s}: Recommendation = {d_res['recommendation']} ({d_res['confidence']}% Conf), Risk = {d_res['risk']}")
    print("[PASS] Decision Agent reasoning synthesis verified.")
    
    print("\n==================================================")
    print("ALL TESTS PASSED SUCCESSFULLY (100% OPERATIONAL)")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
