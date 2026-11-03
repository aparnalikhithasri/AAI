import sys
import os

# Ensure project root is on sys.path for direct script execution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from typing import Dict, Any, List
from services.stock_service import get_latest_price, get_stock_info, get_available_stocks
from database.database import get_cash_balance, get_holdings, get_holding_for_symbol

class RiskAgent:
    """
    Agent 3: Risk Analysis Agent
    Responsible for portfolio risk evaluation, concentration assessment,
    and capital preservation checks.
    """

    def __init__(self):
        self.name = "Risk Analysis Agent"

    def analyze(self, symbol: str, proposed_quantity: int = 10) -> Dict[str, Any]:
        """
        Evaluate investment risk for purchasing proposed_quantity of symbol given
        the current virtual portfolio state in SQLite.
        """
        symbol = symbol.upper()
        info = get_stock_info(symbol)
        current_price = get_latest_price(symbol)
        
        cash_balance = get_cash_balance()
        all_holdings = get_holdings()
        current_holding = get_holding_for_symbol(symbol)
        
        # Calculate current portfolio market value
        all_stocks = get_available_stocks()
        current_prices = {s: get_latest_price(s) for s in all_stocks}
        
        holdings_market_val = sum(
            h['quantity'] * current_prices.get(h['symbol'], h['average_price'])
            for h in all_holdings
        )
        total_portfolio_value = cash_balance + holdings_market_val
        if total_portfolio_value <= 0:
            total_portfolio_value = 1000000.0  # Fallback to initial base

        # Trade calculations
        proposed_investment = round(proposed_quantity * current_price, 2)
        concentration_pct = round((proposed_investment / total_portfolio_value) * 100, 2)
        
        existing_qty = current_holding.get('quantity', 0)
        existing_val = round(existing_qty * current_price, 2)
        post_trade_val = existing_val + proposed_investment
        post_trade_concentration_pct = round((post_trade_val / total_portfolio_value) * 100, 2)
        
        # Risk assessment logic
        risk_score = 1  # Base score 1-10
        reasons: List[str] = []
        
        # 1. Cash affordability check
        if proposed_investment > cash_balance:
            risk_score += 6
            reasons.append(f"Insufficient cash! Trade requires {info['currency']}{proposed_investment:,.2f} but available cash is {info['currency']}{cash_balance:,.2f}.")
        elif proposed_investment > cash_balance * 0.7:
            risk_score += 3
            reasons.append(f"Trade consumes over 70% of available liquid cash ({info['currency']}{cash_balance:,.2f}).")
        else:
            reasons.append(f"Adequate liquidity: trade represents {round((proposed_investment/cash_balance)*100, 1)}% of available cash.")

        # 2. Portfolio concentration check
        if post_trade_concentration_pct > 40:
            risk_score += 4
            reasons.append(f"High single-stock concentration: {symbol} would account for {post_trade_concentration_pct}% of total portfolio.")
        elif post_trade_concentration_pct > 20:
            risk_score += 2
            reasons.append(f"Moderate concentration: {symbol} would represent {post_trade_concentration_pct}% of portfolio value.")
        else:
            reasons.append(f"Prudent allocation: proposed position is {post_trade_concentration_pct}% of total portfolio.")

        # 3. Existing exposure check
        if existing_qty > 0:
            reasons.append(f"Existing position: User already holds {existing_qty} shares of {symbol} (Avg Price: {info['currency']}{current_holding['average_price']:,.2f}).")
        else:
            reasons.append(f"New position: Introduces initial exposure to {info['name']}.")

        # 4. Sector Diversification check
        target_sector = info.get("sector", "General")
        sector_holdings_count = 0
        for h in all_holdings:
            h_info = get_stock_info(h['symbol'])
            if h_info.get("sector") == target_sector:
                sector_holdings_count += 1
                
        if sector_holdings_count > 1 and existing_qty == 0:
            risk_score += 1
            reasons.append(f"Sector overlap: Portfolio already holds other {target_sector} assets.")
        else:
            reasons.append(f"Sector exposure to {target_sector} is well-balanced.")

        # Classify final risk level
        if risk_score >= 6:
            risk_level = "HIGH"
        elif risk_score >= 3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        summary_text = (
            f"Risk Analysis\n"
            f"Risk Level: {risk_level}\n\n"
            f"Reasons:\n" + "\n".join(f"• {r}" for r in reasons)
        )

        return {
            "symbol": symbol,
            "proposed_quantity": proposed_quantity,
            "proposed_investment": proposed_investment,
            "cash_balance": cash_balance,
            "total_portfolio_value": total_portfolio_value,
            "concentration_pct": post_trade_concentration_pct,
            "existing_shares": existing_qty,
            "risk_score": min(10, risk_score),
            "risk_level": risk_level,
            "reasons": reasons,
            "summary_text": summary_text
        }

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    agent = RiskAgent()
    target = sys.argv[1] if len(sys.argv) > 1 else "TCS"
    qty = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    print(f"=== Running Risk Analysis on {target} ({qty} shares) ===")
    res = agent.analyze(target, proposed_quantity=qty)
    print(f"Risk Level: {res['risk_level']} (Score: {res['risk_score']}/10)")
    print(f"Proposed Investment: ₹{res['proposed_investment']:,.2f}")
    print(f"Post-Trade Portfolio Concentration: {res['concentration_pct']}%")
    print("Risk Factors:")
    for r in res['reasons']:
        print(f"  - {r}")


