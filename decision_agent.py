import sys
import os

# Ensure project root is on sys.path for direct script execution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from typing import Dict, Any, List
import re
from services.ollama_service import generate_response, is_ollama_running, is_model_available

class DecisionAgent:
    """
    Agent 4: Decision & Reasoning Agent
    The primary cognitive agent that fuses technical, fundamental/news,
    and portfolio risk perspectives into a final verdict.
    """

    def __init__(self):
        self.name = "Decision Agent"

    def decide(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        news_data: Dict[str, Any],
        risk_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize all multi-agent outputs and produce final recommendation.
        """
        symbol = symbol.upper()
        
        # Format the comprehensive multi-agent context prompt
        prompt = self._construct_prompt(symbol, market_data, news_data, risk_data)
        system_prompt = (
            "You are an expert Chief Investment Officer and Multi-Agent Decision AI. "
            "You synthesize technical market data, news sentiment, and risk analysis "
            "to provide disciplined, rational trading recommendations (BUY, HOLD, or SELL). "
            "Never guarantee profits and strictly follow the requested output format."
        )

        if is_ollama_running() and is_model_available():
            res = generate_response(prompt, system_prompt=system_prompt, temperature=0.2)
            if res.get("success") and res.get("response"):
                parsed = self._parse_llm_decision(res["response"], market_data, news_data, risk_data)
                return parsed

        # Deterministic Multi-Agent Reasoning Fallback (if Ollama is offline)
        return self._fallback_decision(symbol, market_data, news_data, risk_data)

    def _construct_prompt(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        news_data: Dict[str, Any],
        risk_data: Dict[str, Any]
    ) -> str:
        """Build structured multi-agent summary for Llama 3.2:1B."""
        return f"""Synthesize the following 3 agent reports for {symbol} and generate a final recommendation:

=== AGENT 1: MARKET ANALYSIS REPORT ===
- Current Price: {market_data.get('currency', '₹')}{market_data.get('current_price')}
- 20-Day Moving Average: {market_data.get('currency', '₹')}{market_data.get('sma_20')}
- 50-Day Moving Average: {market_data.get('currency', '₹')}{market_data.get('sma_50')}
- RSI (14-Period): {market_data.get('rsi')}
- MACD Line: {market_data.get('macd')} | Signal Line: {market_data.get('macd_signal')}
- Technical Trend: {market_data.get('trend')}

=== AGENT 2: NEWS & SENTIMENT REPORT ===
- Sentiment: {news_data.get('sentiment')}
- News Summary: {news_data.get('summary')}
- Key Catalysts: {', '.join(news_data.get('important_factors', []))}

=== AGENT 3: PORTFOLIO RISK REPORT ===
- Risk Level: {risk_data.get('risk_level')} (Score: {risk_data.get('risk_score')}/10)
- Proposed Investment: {market_data.get('currency', '₹')}{risk_data.get('proposed_investment', 0):,.2f}
- Portfolio Concentration: {risk_data.get('concentration_pct')}%
- Key Risk Factors: {', '.join(risk_data.get('reasons', []))}

=== INSTRUCTIONS ===
Based on the convergence of technical trend, news sentiment, and risk profile:
Provide your final output in EXACTLY this format:

RECOMMENDATION: [BUY or HOLD or SELL]
CONFIDENCE: [Number between 0 and 100]%
RISK: [LOW or MEDIUM or HIGH]
REASONS:
1. [Clear technical reasoning]
2. [Clear news/fundamental reasoning]
3. [Clear portfolio risk rationale]
"""

    def _parse_llm_decision(
        self,
        text: str,
        market_data: Dict[str, Any],
        news_data: Dict[str, Any],
        risk_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse the structured decision text from Llama 3.2:1B."""
        recommendation = "HOLD"
        confidence = 70
        risk = risk_data.get("risk_level", "MEDIUM")
        reasons: List[str] = []

        # 1. Parse Recommendation
        rec_match = re.search(r"RECOMMENDATION:\s*(BUY|HOLD|SELL)", text, re.IGNORECASE)
        if rec_match:
            recommendation = rec_match.group(1).upper()
        elif "BUY" in text.upper() and "SELL" not in text.upper():
            recommendation = "BUY"
        elif "SELL" in text.upper() and "BUY" not in text.upper():
            recommendation = "SELL"

        # 2. Parse Confidence
        conf_match = re.search(r"CONFIDENCE:\s*(\d+)", text)
        if conf_match:
            try:
                confidence = max(10, min(99, int(conf_match.group(1))))
            except ValueError:
                confidence = 75

        # 3. Parse Risk
        risk_match = re.search(r"RISK:\s*(LOW|MEDIUM|HIGH)", text, re.IGNORECASE)
        if risk_match:
            risk = risk_match.group(1).upper()

        # 4. Parse Bulleted Reasons
        reason_lines = re.findall(r"(?:^|\n)(?:\d+\.|\-|\*)\s*(.+)", text)
        for r in reason_lines:
            clean_r = r.strip()
            if clean_r and clean_r not in reasons and not clean_r.startswith("RECOMMENDATION"):
                reasons.append(clean_r)

        if len(reasons) < 2:
            reasons = [
                f"Market Agent indicates a {market_data.get('trend')} technical trend with RSI at {market_data.get('rsi')}.",
                f"News Agent sentiment is {news_data.get('sentiment')} based on recent corporate developments.",
                f"Risk Agent classified portfolio exposure as {risk_data.get('risk_level')} risk."
            ]

        return {
            "symbol": market_data.get("symbol"),
            "recommendation": recommendation,
            "confidence": confidence,
            "risk": risk,
            "reasons": reasons[:4],
            "raw_response": text,
            "ai_powered": True
        }

    def _fallback_decision(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        news_data: Dict[str, Any],
        risk_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deterministic multi-agent reasoning synthesis engine
        used when Ollama is offline or starting up.
        """
        trend = market_data.get("trend", "NEUTRAL")
        sentiment = news_data.get("sentiment", "NEUTRAL")
        risk_lvl = risk_data.get("risk_level", "MEDIUM")
        rsi = market_data.get("rsi", 50.0)

        # Multi-Factor Scoring
        score = 0
        reasons = []

        # Factor 1: Technicals
        if trend == "BULLISH":
            score += 2
            reasons.append(f"Technical indicators are BULLISH with price trading above key moving averages and RSI at {rsi}.")
        elif trend == "BEARISH":
            score -= 2
            reasons.append(f"Technical indicators are BEARISH with downward price momentum and weak moving average support.")
        else:
            reasons.append(f"Technical trend is NEUTRAL; stock is consolidating between support and resistance levels.")

        # Factor 2: News Sentiment
        if sentiment == "POSITIVE":
            score += 2
            reasons.append(f"News sentiment is POSITIVE, driven by favorable contract wins and healthy corporate performance.")
        elif sentiment == "NEGATIVE":
            score -= 2
            reasons.append(f"News sentiment is NEGATIVE due to short-term industry headwinds and margin caution.")
        else:
            reasons.append(f"News flow is balanced with steady operational announcements.")

        # Factor 3: Portfolio Risk
        if risk_lvl == "HIGH":
            score -= 1
            reasons.append(f"Risk Agent flagged HIGH risk due to high portfolio concentration or limited cash liquidity.")
        elif risk_lvl == "LOW":
            score += 1
            reasons.append(f"Risk Agent confirmed LOW risk with sound diversification and ample virtual cash reserve.")
        else:
            reasons.append(f"Portfolio risk is MEDIUM with manageable capital allocation.")

        # Synthesis
        if score >= 3:
            recommendation = "BUY"
            confidence = min(92, 75 + score * 4)
        elif score <= -3:
            recommendation = "SELL"
            confidence = min(90, 75 + abs(score) * 4)
        else:
            recommendation = "HOLD"
            confidence = 68

        return {
            "symbol": symbol,
            "recommendation": recommendation,
            "confidence": confidence,
            "risk": risk_lvl,
            "reasons": reasons,
            "raw_response": "Generated via Multi-Agent Synthesis Engine (Offline Mode)",
            "ai_powered": False
        }

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    from agents.market_agent import MarketAgent
    from agents.news_agent import NewsAgent
    from agents.risk_agent import RiskAgent

    target = sys.argv[1] if len(sys.argv) > 1 else "TCS"
    qty = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    print(f"=== Multi-Agent Orchestration on {target} ({qty} shares) ===")
    m_agent = MarketAgent()
    n_agent = NewsAgent()
    r_agent = RiskAgent()
    d_agent = DecisionAgent()

    m_data = m_agent.analyze(target)
    n_data = n_agent.analyze(target)
    r_data = r_agent.analyze(target, proposed_quantity=qty)
    d_res = d_agent.decide(target, m_data, n_data, r_data)

    print(f"Verdict: {d_res['recommendation']} ({d_res['confidence']}% Confidence)")
    print(f"Risk Assessment: {d_res['risk']}")
    print("Reasoning:")
    for r in d_res['reasons']:
        print(f"  - {r}")


