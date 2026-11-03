import sys
import os

# Ensure project root is on sys.path for direct script execution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from typing import Dict, Any, List
import re
from services.stock_service import load_stock_news, get_stock_info
from services.ollama_service import generate_response, is_ollama_running, is_model_available

class NewsAgent:
    """
    Agent 2: News Analysis Agent
    Responsible for evaluating sentiment and extracting catalysts from local news articles.
    """

    def __init__(self):
        self.name = "News Analysis Agent"

    def analyze(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze news for the given stock symbol using Llama 3.2:1B or deterministic fallback.
        """
        symbol = symbol.upper()
        articles = load_stock_news(symbol)
        info = get_stock_info(symbol)
        
        if not articles:
            return {
                "symbol": symbol,
                "sentiment": "NEUTRAL",
                "summary": f"No recent news articles found for {symbol}.",
                "important_factors": ["No news events recorded in local dataset."],
                "articles_count": 0,
                "articles": [],
                "summary_text": f"News Sentiment: NEUTRAL\nSummary: No recent news available."
            }

        # Prepare formatted news text for LLM analysis
        news_text_list = []
        for i, art in enumerate(articles[:6], 1):
            news_text_list.append(
                f"{i}. [{art.get('category', 'General')}] {art.get('title')} ({art.get('date')}): {art.get('description')}"
            )
        formatted_news = "\n".join(news_text_list)

        # Attempt LLM Analysis with Ollama (Llama 3.2:1B)
        if is_ollama_running() and is_model_available():
            prompt = f"""You are a Financial News Analysis AI Agent. Analyze the following news headlines and descriptions for {symbol} ({info['name']}):

{formatted_news}

Provide your analysis in EXACTLY this format:
SENTIMENT: [POSITIVE or NEUTRAL or NEGATIVE]
SUMMARY: [2-3 sentence overview of the news tone and corporate events]
FACTORS:
- [Key factor 1]
- [Key factor 2]
- [Key factor 3]
"""
            system_prompt = "You are a professional financial news analyst. Be concise, objective, and strictly follow the requested output format."
            
            res = generate_response(prompt, system_prompt=system_prompt, temperature=0.1)
            
            if res.get("success") and res.get("response"):
                parsed = self._parse_llm_response(res["response"], articles)
                return {
                    "symbol": symbol,
                    "sentiment": parsed["sentiment"],
                    "summary": parsed["summary"],
                    "important_factors": parsed["factors"],
                    "articles_count": len(articles),
                    "articles": articles,
                    "summary_text": (
                        f"News Sentiment: {parsed['sentiment']}\n\n"
                        f"Summary:\n{parsed['summary']}\n\n"
                        f"Important Factors:\n" + "\n".join(f"• {f}" for f in parsed["factors"])
                    ),
                    "ai_powered": True
                }

        # Fallback Rule-Based Analysis if Ollama is offline
        fallback_res = self._fallback_analysis(symbol, articles)
        return {
            "symbol": symbol,
            "sentiment": fallback_res["sentiment"],
            "summary": fallback_res["summary"],
            "important_factors": fallback_res["factors"],
            "articles_count": len(articles),
            "articles": articles,
            "summary_text": (
                f"News Sentiment: {fallback_res['sentiment']}\n\n"
                f"Summary:\n{fallback_res['summary']}\n\n"
                f"Important Factors:\n" + "\n".join(f"• {f}" for f in fallback_res["factors"])
            ),
            "ai_powered": False
        }

    def _parse_llm_response(self, text: str, articles: List[Dict]) -> Dict[str, Any]:
        """Extract structured sentiment, summary, and factors from Llama output."""
        sentiment = "NEUTRAL"
        summary = "Recent news indicates steady operational performance."
        factors = []

        # Find sentiment
        sentiment_match = re.search(r"SENTIMENT:\s*(POSITIVE|NEGATIVE|NEUTRAL)", text, re.IGNORECASE)
        if sentiment_match:
            sentiment = sentiment_match.group(1).upper()
        elif "POSITIVE" in text.upper():
            sentiment = "POSITIVE"
        elif "NEGATIVE" in text.upper():
            sentiment = "NEGATIVE"

        # Find summary
        summary_match = re.search(r"SUMMARY:\s*(.*?)(?=\nFACTORS:|\n-|\Z)", text, re.DOTALL | re.IGNORECASE)
        if summary_match and summary_match.group(1).strip():
            summary = summary_match.group(1).strip()

        # Find factors
        factor_lines = re.findall(r"-\s*(.+)", text)
        for fl in factor_lines:
            clean_f = fl.strip()
            if clean_f and clean_f not in factors:
                factors.append(clean_f)

        if not factors:
            factors = [a.get("title", "") for a in articles[:3] if a.get("title")]

        return {
            "sentiment": sentiment,
            "summary": summary,
            "factors": factors[:4]
        }

    def _fallback_analysis(self, symbol: str, articles: List[Dict]) -> Dict[str, Any]:
        """Deterministic news analyzer when Ollama server is unavailable."""
        pos_keywords = ["growth", "deal", "secures", "profit", "surpass", "expand", "dividend", "collaboration", "inaugurates", "rebound", "upgrades", "record", "repurchase"]
        neg_keywords = ["loss", "drop", "pressure", "decline", "fall", "investigation", "penalty", "slump", "friction"]

        pos_count = 0
        neg_count = 0

        for art in articles:
            content = (art.get("title", "") + " " + art.get("description", "")).lower()
            for kw in pos_keywords:
                if kw in content:
                    pos_count += 1
            for kw in neg_keywords:
                if kw in content:
                    neg_count += 1

        if pos_count > neg_count + 1:
            sentiment = "POSITIVE"
            summary = f"Recent news for {symbol} is predominantly positive, highlighting strategic expansion, strong contract momentum, and healthy earnings reports."
        elif neg_count > pos_count + 1:
            sentiment = "NEGATIVE"
            summary = f"Recent news for {symbol} reflects industry headwinds, margin compression, or operational caution."
        else:
            sentiment = "NEUTRAL"
            summary = f"Recent news flow for {symbol} presents a balanced mix of steady core operational updates and routine corporate developments."

        factors = [art.get("title", "") for art in articles[:3]]
        return {
            "sentiment": sentiment,
            "summary": summary,
            "factors": factors
        }

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    agent = NewsAgent()
    target = sys.argv[1] if len(sys.argv) > 1 else "TCS"
    print(f"=== Running News Analysis on {target} ===")
    res = agent.analyze(target)
    print(f"Sentiment: {res['sentiment']}")
    print(f"Summary: {res['summary']}")
    print("Key Factors:")
    for f in res.get('important_factors', []):
        print(f"  - {f}")


