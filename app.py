"""
Reasoning Is All You Need: A Multi-Agent AI System for Intelligent Stock Analysis and Paper Trading
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# Internal project modules
from services.stock_service import (
    get_available_stocks,
    get_stock_info,
    load_stock_data,
    get_stock_summary,
    load_stock_news,
    get_latest_price
)
from services.ollama_service import is_ollama_running, is_model_available, DEFAULT_MODEL
from database.database import (
    init_db,
    get_cash_balance,
    get_holdings,
    get_holding_for_symbol,
    get_transactions,
    execute_buy,
    execute_sell,
    get_portfolio_summary,
    reset_portfolio
)
from agents.market_agent import MarketAgent
from agents.news_agent import NewsAgent
from agents.risk_agent import RiskAgent
from agents.decision_agent import DecisionAgent

# Initialize DB on start
init_db()

# Page configuration
st.set_page_config(
    page_title="Reasoning Is All You Need | Multi-Agent AI Stock System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for modern dark theme
st.markdown("""
<style>
    /* Global styles */
    .main {
        background-color: #0e1117;
    }
    
    /* Card container */
    .metric-card {
        background: linear-gradient(135deg, #1e222d 0%, #252a38 100%);
        border: 1px solid #2d3345;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        margin-bottom: 15px;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #9aa0a6;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    
    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    .metric-sub {
        font-size: 0.85rem;
        margin-top: 4px;
    }
    
    .positive-text {
        color: #00c853 !important;
    }
    
    .negative-text {
        color: #ff5252 !important;
    }
    
    .neutral-text {
        color: #ffb300 !important;
    }

    /* Decision banner */
    .decision-banner-buy {
        background: linear-gradient(135deg, #0d3b24 0%, #165b38 100%);
        border: 2px solid #00c853;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .decision-banner-sell {
        background: linear-gradient(135deg, #441118 0%, #6e1d28 100%);
        border: 2px solid #ff5252;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .decision-banner-hold {
        background: linear-gradient(135deg, #3d310d 0%, #635016 100%);
        border: 2px solid #ffb300;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .decision-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin: 0;
    }
    
    .agent-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }
    
    .news-card {
        background-color: #1a1e29;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    
    .demo-notice {
        background-color: #132238;
        border: 1px solid #1e3a8a;
        color: #93c5fd;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 0.88rem;
        margin-bottom: 18px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to get current stock prices
def get_current_prices_map():
    stocks = get_available_stocks()
    return {s: get_latest_price(s) for s in stocks}

# Sidebar Navigation & Status
st.sidebar.markdown("# 🧠 Reasoning Is All You Need")
st.sidebar.caption("Multi-Agent AI Stock Analysis & Paper Trading")

# Ollama Status in Sidebar
ollama_active = is_ollama_running()
model_active = is_model_available(DEFAULT_MODEL) if ollama_active else False

if ollama_active and model_active:
    st.sidebar.success(f"🟢 Ollama Online ({DEFAULT_MODEL})")
elif ollama_active:
    st.sidebar.warning(f"🟡 Ollama Active (Pull {DEFAULT_MODEL})")
else:
    st.sidebar.info("🔵 Offline Agent Mode (Ollama fallback)")

page = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Dashboard",
        "📈 Stock Analysis",
        "🤖 AI Advisor",
        "💸 Paper Trading",
        "💼 Portfolio",
        "📜 Transactions"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ System Overview")
st.sidebar.markdown("""
- **Agent 1:** Market Agent *(Technicals)*
- **Agent 2:** News Agent *(Sentiment)*
- **Agent 3:** Risk Agent *(Concentration)*
- **Agent 4:** Decision Agent *(Synthesis)*
- **Model:** Llama 3.2:1B (Local)
- **Database:** SQLite
""")

# ==========================================
# 1. DASHBOARD PAGE
# ==========================================
if page == "📊 Dashboard":
    st.title("📊 Virtual Trading Dashboard")
    st.markdown("Overview of your paper-trading portfolio, asset allocation, and recent market movements.")
    
    current_prices = get_current_prices_map()
    summary = get_portfolio_summary(current_prices)
    
    # Key Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Available Cash</div>
            <div class="metric-value">₹{summary['cash_balance']:,.2f}</div>
            <div class="metric-sub text-muted">Virtual Liquid Capital</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Portfolio Value</div>
            <div class="metric-value">₹{summary['portfolio_value']:,.2f}</div>
            <div class="metric-sub text-muted">Holdings + Cash</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        pl_class = "positive-text" if summary['unrealized_pl'] >= 0 else "negative-text"
        sign = "+" if summary['unrealized_pl'] >= 0 else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Profit / Loss</div>
            <div class="metric-value {pl_class}">{sign}₹{summary['unrealized_pl']:,.2f}</div>
            <div class="metric-sub {pl_class}">{sign}{summary['unrealized_pl_pct']:.2f}% Unrealized Return</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Active Holdings</div>
            <div class="metric-value">{summary['holdings_count']}</div>
            <div class="metric-sub text-muted">Invested: ₹{summary['invested_capital']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Portfolio Allocation and Market Watch
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("🥧 Asset Allocation")
        if summary['holdings_count'] == 0:
            # 100% Cash pie chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Cash'],
                values=[summary['cash_balance']],
                hole=0.5,
                marker_colors=['#00c853']
            )])
        else:
            labels = ['Cash'] + [h['symbol'] for h in summary['holdings']]
            values = [summary['cash_balance']] + [h['current_value'] for h in summary['holdings']]
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.5,
                textinfo='label+percent',
                marker=dict(colors=['#00c853', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'])
            )])
            
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            margin=dict(l=10, r=10, t=20, b=20),
            showlegend=True
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_right:
        st.subheader("⚡ Available Stocks Quick Watch")
        stocks = get_available_stocks()
        watch_data = []
        for s in stocks:
            sm = get_stock_summary(s)
            watch_data.append({
                "Stock": s,
                "Company": sm["name"],
                "Price": f"{sm['currency']}{sm['current_price']:,.2f}",
                "Change": f"{sm['change']:+.2f} ({sm['change_pct']:+.2f}%)",
                "RSI (14)": sm["rsi"],
                "20-Day MA": f"{sm['currency']}{sm['sma_20']:,.2f}"
            })
        st.dataframe(pd.DataFrame(watch_data), hide_index=True, use_container_width=True)

    # Current Holdings Table
    st.subheader("💼 Current Stock Positions")
    if summary['holdings_count'] == 0:
        st.info("You do not hold any stocks currently. Go to **Paper Trading** or **AI Advisor** to make your first trade!")
    else:
        h_df = pd.DataFrame(summary['holdings'])
        h_display = pd.DataFrame({
            "Stock": h_df['symbol'],
            "Quantity": h_df['quantity'],
            "Avg Buy Price": h_df['average_price'].map(lambda x: f"₹{x:,.2f}"),
            "Current Price": h_df['current_price'].map(lambda x: f"₹{x:,.2f}"),
            "Invested Value": h_df['invested_value'].map(lambda x: f"₹{x:,.2f}"),
            "Current Value": h_df['current_value'].map(lambda x: f"₹{x:,.2f}"),
            "Profit / Loss": h_df['profit_loss'].map(lambda x: f"{'+' if x>=0 else ''}₹{x:,.2f}"),
            "Return %": h_df['profit_loss_pct'].map(lambda x: f"{'+' if x>=0 else ''}{x:.2f}%")
        })
        st.dataframe(h_display, hide_index=True, use_container_width=True)

# ==========================================
# 2. STOCK ANALYSIS PAGE
# ==========================================
elif page == "📈 Stock Analysis":
    st.title("📈 Technical & Fundamental Stock Analysis")
    
    stocks = get_available_stocks()
    selected_stock = st.selectbox("Select Stock for Deep Analysis:", stocks, index=0)
    
    stock_info = get_stock_info(selected_stock)
    summary = get_stock_summary(selected_stock)
    df = load_stock_data(selected_stock, with_indicators=True)
    
    st.markdown(f"**{stock_info['name']}** | Sector: `{stock_info['sector']}`")
    st.caption(stock_info['description'])
    
    # Key metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric(
            label="Current Price",
            value=f"{summary['currency']}{summary['current_price']:,.2f}",
            delta=f"{summary['change']:+.2f} ({summary['change_pct']:+.2f}%)"
        )
    with m2:
        st.metric(label="20-Day SMA", value=f"{summary['currency']}{summary['sma_20']:,.2f}")
    with m3:
        st.metric(label="50-Day SMA", value=f"{summary['currency']}{summary['sma_50']:,.2f}")
    with m4:
        rsi_val = summary['rsi']
        rsi_status = "Overbought" if rsi_val > 70 else ("Oversold" if rsi_val < 30 else "Neutral")
        st.metric(label="RSI (14)", value=f"{rsi_val:.1f}", delta=rsi_status, delta_color="off")
    with m5:
        macd_val = summary['macd']
        st.metric(label="MACD (12,26,9)", value=f"{macd_val:.2f}", delta=f"Signal: {summary['macd_signal']:.2f}")

    # Interactive Plotly Candlestick & Technical Charts
    st.subheader(f"📊 {selected_stock} Technical Charts")
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f"{selected_stock} Price & Moving Averages", "Relative Strength Index (RSI 14)", "MACD & Histogram")
    )
    
    # 1. Candlestick & MAs
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price OHLC',
        increasing_line_color='#00c853',
        decreasing_line_color='#ff5252'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['SMA_20'],
        name='20-Day SMA',
        line=dict(color='#f59e0b', width=1.5)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['SMA_50'],
        name='50-Day SMA',
        line=dict(color='#3b82f6', width=1.5)
    ), row=1, col=1)
    
    # 2. RSI Subplot
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['RSI'],
        name='RSI',
        line=dict(color='#a855f7', width=1.5)
    ), row=2, col=1)
    
    # RSI threshold lines (70 overbought, 30 oversold)
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#22c55e", row=2, col=1)
    
    # 3. MACD Subplot
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['MACD'],
        name='MACD Line',
        line=dict(color='#38bdf8', width=1.5)
    ), row=3, col=1)
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['MACD_Signal'],
        name='Signal Line',
        line=dict(color='#f97316', width=1.5)
    ), row=3, col=1)
    
    colors = ['#22c55e' if h >= 0 else '#ef4444' for h in df['MACD_Hist']]
    fig.add_trace(go.Bar(
        x=df['Date'],
        y=df['MACD_Hist'],
        name='MACD Hist',
        marker_color=colors
    ), row=3, col=1)
    
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        paper_bgcolor='#131722',
        plot_bgcolor='#131722',
        height=650,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Market Agent Technical Summary
    market_agent = MarketAgent()
    market_res = market_agent.analyze(selected_stock)
    
    st.subheader(f"🤖 Market Agent Quantitative Verdict")
    trend_color = "#00c853" if market_res["trend"] == "BULLISH" else ("#ff5252" if market_res["trend"] == "BEARISH" else "#ffb300")
    
    st.markdown(f"""
    <div style="background-color: #1a1e29; border: 1px solid #2d3345; border-radius: 10px; padding: 18px; margin-bottom: 20px;">
        <h4 style="margin: 0; color: #ffffff;">Technical Trend: <span style="color: {trend_color}; font-weight: bold;">{market_res['trend']}</span></h4>
        <ul style="margin-top: 10px; margin-bottom: 0; color: #e2e8f0;">
            {''.join(f'<li>{sig}</li>' for sig in market_res['signals'])}
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # News & Sentiment Section
    st.subheader(f"📰 Local News & Catalysts ({selected_stock})")
    news_items = load_stock_news(selected_stock)
    
    if not news_items:
        st.info(f"No recent news articles recorded for {selected_stock}.")
    else:
        for item in news_items:
            cat = item.get("category", "General")
            st.markdown(f"""
            <div class="news-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="background-color: #2563eb; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">{cat}</span>
                    <span style="color: #94a3b8; font-size: 0.8rem;">{item.get('date')}</span>
                </div>
                <h5 style="margin: 8px 0 4px 0; color: #f8fafc;">{item.get('title')}</h5>
                <p style="margin: 0; color: #cbd5e1; font-size: 0.9rem;">{item.get('description')}</p>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 3. AI ADVISOR PAGE
# ==========================================
elif page == "🤖 AI Advisor":
    st.title("🤖 Multi-Agent AI Investment Advisor")
    st.markdown("Coordinate all 4 specialized AI agents and Llama 3.2:1B to evaluate market data, news sentiment, and portfolio risk.")
    
    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        stocks = get_available_stocks()
        target_stock = st.selectbox("Select Target Stock:", stocks, index=0)
    with col_s2:
        prop_qty = st.number_input("Proposed Trade Quantity:", min_value=1, max_value=500, value=10, step=1)
        
    stock_info = get_stock_info(target_stock)
    latest_price = get_latest_price(target_stock)
    est_investment = round(prop_qty * latest_price, 2)
    cash_bal = get_cash_balance()
    
    st.markdown(f"**Current Price:** `{stock_info['currency']}{latest_price:,.2f}` | **Estimated Order Cost:** `{stock_info['currency']}{est_investment:,.2f}` | **Available Cash:** `₹{cash_bal:,.2f}`")
    
    if st.button("🚀 Run Multi-Agent Analysis", type="primary", use_container_width=True):
        with st.status("🧠 Multi-Agent Collaborative Reasoning in Progress...", expanded=True) as status:
            # 1. Market Agent
            st.write("📊 **Step 1/4: Market Analysis Agent** computing 20-MA, 50-MA, RSI, and MACD indicators...")
            market_agent = MarketAgent()
            market_data = market_agent.analyze(target_stock)
            st.write(f"✓ Market Agent identified trend: **{market_data['trend']}**")
            
            # 2. News Agent
            st.write("📰 **Step 2/4: News Analysis Agent** scanning local news & evaluating sentiment...")
            news_agent = NewsAgent()
            news_data = news_agent.analyze(target_stock)
            st.write(f"✓ News Agent assessed sentiment: **{news_data['sentiment']}**")
            
            # 3. Risk Agent
            st.write("⚖️ **Step 3/4: Risk Analysis Agent** checking cash liquidity & portfolio concentration...")
            risk_agent = RiskAgent()
            risk_data = risk_agent.analyze(target_stock, proposed_quantity=prop_qty)
            st.write(f"✓ Risk Agent classified portfolio risk: **{risk_data['risk_level']}** (Score: {risk_data['risk_score']}/10)")
            
            # 4. Decision Agent + Ollama
            st.write("🤖 **Step 4/4: Decision Agent** orchestrating synthesis via Llama 3.2:1B...")
            decision_agent = DecisionAgent()
            decision_data = decision_agent.decide(target_stock, market_data, news_data, risk_data)
            
            status.update(label="✅ Multi-Agent Reasoning Complete!", state="complete", expanded=False)
            
        # Store in session state for display
        st.session_state["latest_analysis"] = {
            "symbol": target_stock,
            "market_data": market_data,
            "news_data": news_data,
            "risk_data": risk_data,
            "decision_data": decision_data
        }

    # Display Analysis Results if available
    if "latest_analysis" in st.session_state and st.session_state["latest_analysis"]["symbol"] == target_stock:
        res = st.session_state["latest_analysis"]
        dec = res["decision_data"]
        mkt = res["market_data"]
        news = res["news_data"]
        risk = res["risk_data"]
        
        rec = dec["recommendation"]
        conf = dec["confidence"]
        risk_lvl = dec["risk"]
        
        banner_class = "decision-banner-buy" if rec == "BUY" else ("decision-banner-sell" if rec == "SELL" else "decision-banner-hold")
        banner_color = "#00c853" if rec == "BUY" else ("#ff5252" if rec == "SELL" else "#ffb300")
        
        st.markdown("---")
        # Recommendation Banner
        st.markdown(f"""
        <div class="{banner_class}">
            <div style="font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; color: #e2e8f0; margin-bottom: 4px;">AI Multi-Agent Consensus</div>
            <div class="decision-title" style="color: {banner_color};">{rec}</div>
            <div style="font-size: 1.2rem; font-weight: 600; margin-top: 8px; color: #ffffff;">
                {conf}% Confidence &nbsp;•&nbsp; <span style="padding: 3px 10px; border-radius: 6px; background-color: rgba(255,255,255,0.1);">{risk_lvl} RISK</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Reasoning Section
        st.subheader("💡 Why this recommendation?")
        for i, reason in enumerate(dec["reasons"], 1):
            st.markdown(f"**{i}.** {reason}")
            
        # Quick Paper Trade Execution Card
        st.markdown("---")
        st.subheader("⚡ Quick Paper Action")
        qp_col1, qp_col2 = st.columns([2, 1])
        with qp_col1:
            st.markdown(f"Instantly execute a paper **{rec}** order for **{prop_qty} shares of {target_stock}** at `₹{latest_price:,.2f}` (Total: `₹{est_investment:,.2f}`).")
        with qp_col2:
            if rec == "BUY":
                if st.button(f"🛒 Execute Paper BUY ({prop_qty} {target_stock})", type="primary", use_container_width=True):
                    success, msg, _ = execute_buy(target_stock, prop_qty, latest_price)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            elif rec == "SELL":
                if st.button(f"💰 Execute Paper SELL ({prop_qty} {target_stock})", type="primary", use_container_width=True):
                    success, msg, _ = execute_sell(target_stock, prop_qty, latest_price)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.info("AI suggests HOLD. No urgent trade needed.")
        
        # Deep Agent Inspector
        st.markdown("---")
        st.subheader("🔍 Deep Agent Inspector")
        tab1, tab2, tab3 = st.tabs(["📊 Market Agent Details", "📰 News Agent Details", "⚖️ Risk Agent Details"])
        
        with tab1:
            st.markdown(f"**Trend:** `{mkt['trend']}` | **20-MA:** `₹{mkt['sma_20']}` | **50-MA:** `₹{mkt['sma_50']}` | **RSI:** `{mkt['rsi']}` | **MACD:** `{mkt['macd']}`")
            st.markdown("**Key Signals:**")
            for sig in mkt["signals"]:
                st.markdown(f"- {sig}")
                
        with tab2:
            st.markdown(f"**Sentiment:** `{news['sentiment']}` | **Scanned Articles:** `{news['articles_count']}`")
            st.markdown(f"**AI Summary:** {news['summary']}")
            st.markdown("**Important Catalysts:**")
            for f in news.get("important_factors", []):
                st.markdown(f"- {f}")
                
        with tab3:
            st.markdown(f"**Risk Level:** `{risk['risk_level']}` | **Concentration:** `{risk['concentration_pct']}%` | **Risk Score:** `{risk['risk_score']}/10`")
            st.markdown("**Risk Considerations:**")
            for r in risk["reasons"]:
                st.markdown(f"- {r}")

# ==========================================
# 4. PAPER TRADING PAGE
# ==========================================
elif page == "💸 Paper Trading":
    st.title("💸 Paper Trading Terminal")
    st.markdown("Practice trading stocks in real-time with **₹10,00,000** virtual paper money. No real capital at risk.")
    
    current_prices = get_current_prices_map()
    cash_bal = get_cash_balance()
    
    # Overview cards
    c_a, c_b = st.columns(2)
    with c_a:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Virtual Cash Available</div>
            <div class="metric-value">₹{cash_bal:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c_b:
        stocks = get_available_stocks()
        selected_stock = st.selectbox("Select Asset to Trade:", stocks, index=0)
        curr_price = current_prices[selected_stock]
        holding_info = get_holding_for_symbol(selected_stock)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{selected_stock} Market Price & Holding</div>
            <div class="metric-value">₹{curr_price:,.2f}</div>
            <div class="metric-sub text-muted">You own: <strong>{holding_info['quantity']} shares</strong> (Avg: ₹{holding_info['average_price']:,.2f})</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📝 Order Execution Form")
    
    form_col1, form_col2 = st.columns([1, 1])
    
    with form_col1:
        action = st.radio("Select Action:", ["BUY", "SELL"], horizontal=True)
        quantity = st.number_input("Quantity of Shares:", min_value=1, max_value=5000, value=10, step=1)
        order_total = round(quantity * curr_price, 2)
        
        st.markdown(f"### Total Order Value: `₹{order_total:,.2f}`")
        
        if action == "BUY" and order_total > cash_bal:
            st.error(f"⚠️ Insufficient Cash! Need ₹{order_total:,.2f} but you have ₹{cash_bal:,.2f}.")
        elif action == "SELL" and quantity > holding_info['quantity']:
            st.error(f"⚠️ Insufficient Shares! You only hold {holding_info['quantity']} shares of {selected_stock}.")
            
        execute_button = st.button(f"⚡ EXECUTE PAPER {action}", type="primary", use_container_width=True)
        
    with form_col2:
        st.markdown("#### 📋 Order Summary Preview")
        st.markdown(f"""
        - **Asset:** `{selected_stock}`
        - **Action:** `{action}`
        - **Unit Price:** `₹{curr_price:,.2f}`
        - **Shares:** `{quantity}`
        - **Gross Value:** `₹{order_total:,.2f}`
        - **Brokerage / Fees:** `₹0.00 (Demo Zero-Fee)`
        - **Estimated Remaining Cash:** `₹{(cash_bal - order_total if action == 'BUY' else cash_bal + order_total):,.2f}`
        """)

    if execute_button:
        if action == "BUY":
            success, msg, payload = execute_buy(selected_stock, quantity, curr_price)
            if success:
                st.success(f"🎉 **BUY ORDER EXECUTED!**\nPurchased {quantity} shares of {selected_stock} at ₹{curr_price:,.2f}. Remaining cash: ₹{payload.get('remaining_cash', 0):,.2f}")
                st.balloons()
            else:
                st.error(f"❌ **ORDER FAILED:** {msg}")
        else:
            success, msg, payload = execute_sell(selected_stock, quantity, curr_price)
            if success:
                st.success(f"🎉 **SELL ORDER EXECUTED!**\nSold {quantity} shares of {selected_stock} at ₹{curr_price:,.2f}. Realized P/L: ₹{payload.get('realized_pl', 0):,.2f}. Remaining cash: ₹{payload.get('remaining_cash', 0):,.2f}")
                st.balloons()
            else:
                st.error(f"❌ **ORDER FAILED:** {msg}")

# ==========================================
# 5. PORTFOLIO PAGE
# ==========================================
elif page == "💼 Portfolio":
    st.title("💼 Virtual Portfolio Management")
    st.markdown("Detailed breakdown of your asset holdings, invested capital, and live performance metrics.")
    
    current_prices = get_current_prices_map()
    summary = get_portfolio_summary(current_prices)
    
    # Portfolio overview banner
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Total Portfolio Value", f"₹{summary['portfolio_value']:,.2f}")
    with p2:
        st.metric("Available Cash", f"₹{summary['cash_balance']:,.2f}")
    with p3:
        st.metric("Invested Capital", f"₹{summary['invested_capital']:,.2f}")
    with p4:
        sign = "+" if summary['unrealized_pl'] >= 0 else ""
        st.metric("Net Unrealized P/L", f"{sign}₹{summary['unrealized_pl']:,.2f}", delta=f"{sign}{summary['unrealized_pl_pct']:.2f}%")
        
    st.markdown("---")
    st.subheader("📊 Positions Breakdown")
    
    if summary['holdings_count'] == 0:
        st.info("No active positions in your portfolio. Use **Paper Trading** or **AI Advisor** to acquire assets.")
    else:
        h_df = pd.DataFrame(summary['holdings'])
        h_table = pd.DataFrame({
            "Symbol": h_df['symbol'],
            "Quantity": h_df['quantity'],
            "Average Buy Price": h_df['average_price'].map(lambda x: f"₹{x:,.2f}"),
            "Current Market Price": h_df['current_price'].map(lambda x: f"₹{x:,.2f}"),
            "Total Invested": h_df['invested_value'].map(lambda x: f"₹{x:,.2f}"),
            "Current Market Value": h_df['current_value'].map(lambda x: f"₹{x:,.2f}"),
            "Unrealized P/L": h_df['profit_loss'].map(lambda x: f"{'+' if x>=0 else ''}₹{x:,.2f}"),
            "Return %": h_df['profit_loss_pct'].map(lambda x: f"{'+' if x>=0 else ''}{x:.2f}%")
        })
        st.dataframe(h_table, hide_index=True, use_container_width=True)

    # Danger Zone: Reset Portfolio
    st.markdown("---")
    st.subheader("⚙️ Portfolio Controls")
    with st.expander("🔄 Reset Virtual Portfolio (Demo/Lab Viva Reset)"):
        st.warning("This will clear all holdings, wipe transaction history, and reset virtual cash to ₹10,00,000.")
        if st.button("Reset to Default ₹10,00,000", type="secondary"):
            reset_portfolio()
            st.success("Portfolio successfully reset to fresh state!")
            st.rerun()

# ==========================================
# 6. TRANSACTIONS PAGE
# ==========================================
elif page == "📜 Transactions":
    st.title("📜 Transaction Audit Log")
    st.markdown("Complete history of all virtual paper-trading BUY and SELL orders recorded in SQLite.")
    
    txs = get_transactions()
    
    if not txs:
        st.info("No transactions recorded yet. Execute trades via **Paper Trading** or **AI Advisor** to see them here.")
    else:
        tx_df = pd.DataFrame(txs)
        
        # Display summary counts
        c_t1, c_t2, c_t3 = st.columns(3)
        with c_t1:
            st.metric("Total Transactions", len(tx_df))
        with c_t2:
            buys_count = len(tx_df[tx_df['type'] == 'BUY'])
            st.metric("Total BUY Orders", buys_count)
        with c_t3:
            sells_count = len(tx_df[tx_df['type'] == 'SELL'])
            st.metric("Total SELL Orders", sells_count)
            
        st.markdown("---")
        
        # Formatted transaction table
        display_tx = pd.DataFrame({
            "Transaction ID": tx_df['id'],
            "Timestamp": tx_df['timestamp'],
            "Stock": tx_df['symbol'],
            "Order Type": tx_df['type'],
            "Quantity": tx_df['quantity'],
            "Executed Price": tx_df['price'].map(lambda x: f"₹{x:,.2f}"),
            "Total Amount": tx_df['total'].map(lambda x: f"₹{x:,.2f}")
        })
        
        st.dataframe(display_tx, hide_index=True, use_container_width=True)
