"""
SQLite Database Module for 'Reasoning Is All You Need'
Manages virtual paper-trading cash, holdings, and transaction history.
"""

import sqlite3
import os
import datetime
from typing import Dict, List, Tuple, Any

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "portfolio.db")
INITIAL_CASH = 1000000.0  # ₹10,00,000 Initial Virtual Cash

def get_connection() -> sqlite3.Connection:
    """Get SQLite connection with row factory."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite tables for paper trading."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Portfolio Meta (Cash Balance)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_meta (
            key TEXT PRIMARY KEY,
            value REAL NOT NULL
        )
    """)
    
    # Holdings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            quantity INTEGER NOT NULL,
            average_price REAL NOT NULL
        )
    """)
    
    # Transactions history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    
    # Initialize Cash Balance if not present
    cursor.execute("SELECT value FROM portfolio_meta WHERE key = 'cash_balance'")
    row = cursor.fetchone()
    if row is None:
        cursor.execute("INSERT INTO portfolio_meta (key, value) VALUES ('cash_balance', ?)", (INITIAL_CASH,))
        cursor.execute("INSERT INTO portfolio_meta (key, value) VALUES ('initial_cash', ?)", (INITIAL_CASH,))
        
    conn.commit()
    conn.close()

def get_cash_balance() -> float:
    """Retrieve available virtual cash balance."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM portfolio_meta WHERE key = 'cash_balance'")
    row = cursor.fetchone()
    conn.close()
    return float(row['value']) if row else INITIAL_CASH

def set_cash_balance(new_balance: float):
    """Update cash balance in database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE portfolio_meta SET value = ? WHERE key = 'cash_balance'", (new_balance,))
    conn.commit()
    conn.close()

def get_holdings() -> List[Dict[str, Any]]:
    """Retrieve all current stock holdings."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT symbol, quantity, average_price FROM holdings WHERE quantity > 0 ORDER BY symbol ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_holding_for_symbol(symbol: str) -> Dict[str, Any]:
    """Retrieve holding information for a specific stock."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT symbol, quantity, average_price FROM holdings WHERE symbol = ?", (symbol.upper(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"symbol": symbol.upper(), "quantity": 0, "average_price": 0.0}

def get_transactions() -> List[Dict[str, Any]]:
    """Retrieve all transactions ordered by latest first."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, symbol, type, quantity, price, total, timestamp FROM transactions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def execute_buy(symbol: str, quantity: int, price: float) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Execute a virtual paper-trading BUY order.
    Validates cash balance, updates holdings, deducts cash, and logs transaction.
    """
    if quantity <= 0:
        return False, "Quantity must be greater than 0.", {}
    if price <= 0:
        return False, "Stock price must be greater than 0.", {}
        
    init_db()
    symbol = symbol.upper()
    total_cost = round(quantity * price, 2)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check cash balance
        cursor.execute("SELECT value FROM portfolio_meta WHERE key = 'cash_balance'")
        cash_row = cursor.fetchone()
        current_cash = float(cash_row['value']) if cash_row else 0.0
        
        if current_cash < total_cost:
            conn.close()
            return False, f"Insufficient virtual cash! Required: ₹{total_cost:,.2f}, Available: ₹{current_cash:,.2f}", {}
            
        new_cash = round(current_cash - total_cost, 2)
        cursor.execute("UPDATE portfolio_meta SET value = ? WHERE key = 'cash_balance'", (new_cash,))
        
        # Check existing holdings
        cursor.execute("SELECT quantity, average_price FROM holdings WHERE symbol = ?", (symbol,))
        holding_row = cursor.fetchone()
        
        if holding_row:
            existing_qty = int(holding_row['quantity'])
            existing_avg = float(holding_row['average_price'])
            
            new_qty = existing_qty + quantity
            new_avg_price = round(((existing_qty * existing_avg) + total_cost) / new_qty, 2)
            
            cursor.execute(
                "UPDATE holdings SET quantity = ?, average_price = ? WHERE symbol = ?",
                (new_qty, new_avg_price, symbol)
            )
        else:
            cursor.execute(
                "INSERT INTO holdings (symbol, quantity, average_price) VALUES (?, ?, ?)",
                (symbol, quantity, price)
            )
            
        # Record Transaction
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO transactions (symbol, type, quantity, price, total, timestamp) VALUES (?, 'BUY', ?, ?, ?, ?)",
            (symbol, quantity, price, total_cost, now_str)
        )
        
        conn.commit()
        conn.close()
        
        result_payload = {
            "symbol": symbol,
            "type": "BUY",
            "quantity": quantity,
            "price": price,
            "total": total_cost,
            "remaining_cash": new_cash,
            "timestamp": now_str
        }
        return True, f"Successfully purchased {quantity} shares of {symbol} at ₹{price:,.2f}!", result_payload
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Database error during BUY: {str(e)}", {}

def execute_sell(symbol: str, quantity: int, price: float) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Execute a virtual paper-trading SELL order.
    Validates share availability, updates holdings, adds cash, and logs transaction.
    """
    if quantity <= 0:
        return False, "Quantity must be greater than 0.", {}
    if price <= 0:
        return False, "Stock price must be greater than 0.", {}
        
    init_db()
    symbol = symbol.upper()
    total_proceeds = round(quantity * price, 2)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check existing holdings
        cursor.execute("SELECT quantity, average_price FROM holdings WHERE symbol = ?", (symbol,))
        holding_row = cursor.fetchone()
        
        if not holding_row or int(holding_row['quantity']) < quantity:
            avail_qty = int(holding_row['quantity']) if holding_row else 0
            conn.close()
            return False, f"Insufficient shares! You own {avail_qty} shares of {symbol}, cannot sell {quantity}.", {}
            
        existing_qty = int(holding_row['quantity'])
        existing_avg = float(holding_row['average_price'])
        
        # Update or delete holding
        if existing_qty == quantity:
            cursor.execute("DELETE FROM holdings WHERE symbol = ?", (symbol,))
        else:
            new_qty = existing_qty - quantity
            cursor.execute("UPDATE holdings SET quantity = ? WHERE symbol = ?", (new_qty, symbol))
            
        # Update cash balance
        cursor.execute("SELECT value FROM portfolio_meta WHERE key = 'cash_balance'")
        cash_row = cursor.fetchone()
        current_cash = float(cash_row['value']) if cash_row else 0.0
        new_cash = round(current_cash + total_proceeds, 2)
        cursor.execute("UPDATE portfolio_meta SET value = ? WHERE key = 'cash_balance'", (new_cash,))
        
        # Record Transaction
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO transactions (symbol, type, quantity, price, total, timestamp) VALUES (?, 'SELL', ?, ?, ?, ?)",
            (symbol, quantity, price, total_proceeds, now_str)
        )
        
        conn.commit()
        conn.close()
        
        realized_pl = round((price - existing_avg) * quantity, 2)
        
        result_payload = {
            "symbol": symbol,
            "type": "SELL",
            "quantity": quantity,
            "price": price,
            "total": total_proceeds,
            "realized_pl": realized_pl,
            "remaining_cash": new_cash,
            "timestamp": now_str
        }
        return True, f"Successfully sold {quantity} shares of {symbol} at ₹{price:,.2f}!", result_payload
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Database error during SELL: {str(e)}", {}

def get_portfolio_summary(current_prices: Dict[str, float]) -> Dict[str, Any]:
    """
    Compute comprehensive portfolio metrics given a dictionary of latest stock prices.
    """
    cash = get_cash_balance()
    raw_holdings = get_holdings()
    
    holdings_list = []
    total_invested_cost = 0.0
    total_current_holdings_value = 0.0
    
    for h in raw_holdings:
        sym = h['symbol']
        qty = h['quantity']
        avg_price = h['average_price']
        curr_price = current_prices.get(sym, avg_price)
        
        invested = round(qty * avg_price, 2)
        curr_val = round(qty * curr_price, 2)
        pl = round(curr_val - invested, 2)
        pl_pct = round((pl / invested) * 100, 2) if invested > 0 else 0.0
        
        total_invested_cost += invested
        total_current_holdings_value += curr_val
        
        holdings_list.append({
            "symbol": sym,
            "quantity": qty,
            "average_price": avg_price,
            "current_price": curr_price,
            "invested_value": invested,
            "current_value": curr_val,
            "profit_loss": pl,
            "profit_loss_pct": pl_pct
        })
        
    total_portfolio_value = round(cash + total_current_holdings_value, 2)
    total_unrealized_pl = round(total_current_holdings_value - total_invested_cost, 2)
    total_unrealized_pl_pct = round((total_unrealized_pl / total_invested_cost) * 100, 2) if total_invested_cost > 0 else 0.0
    
    overall_net_return = round(total_portfolio_value - INITIAL_CASH, 2)
    overall_net_return_pct = round((overall_net_return / INITIAL_CASH) * 100, 2)
    
    return {
        "cash_balance": cash,
        "invested_capital": round(total_invested_cost, 2),
        "holdings_value": round(total_current_holdings_value, 2),
        "portfolio_value": total_portfolio_value,
        "initial_capital": INITIAL_CASH,
        "unrealized_pl": total_unrealized_pl,
        "unrealized_pl_pct": total_unrealized_pl_pct,
        "net_return": overall_net_return,
        "net_return_pct": overall_net_return_pct,
        "holdings_count": len(holdings_list),
        "holdings": holdings_list
    }

def reset_portfolio(initial_cash: float = INITIAL_CASH):
    """Reset virtual portfolio to fresh initial state."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM holdings")
    cursor.execute("DELETE FROM transactions")
    cursor.execute("UPDATE portfolio_meta SET value = ? WHERE key = 'cash_balance'", (initial_cash,))
    conn.commit()
    conn.close()
