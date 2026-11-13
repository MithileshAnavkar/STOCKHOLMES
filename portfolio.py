"""portfolio.py - all the maths and data handling (no UI code here).

The portfolio is stored as a simple dictionary: {"AAPL": 10, "TSLA": 5}
Using a dictionary also guarantees there are no duplicate stock entries.
"""
import pandas as pd
from stock_data import STOCK_PRICES, STOCK_NAMES

COLUMNS = ["Symbol", "Name", "Quantity", "Price", "Investment", "Share"]


def add_stock(holdings, symbol, quantity):
    """Add shares. If the stock already exists, quantities are merged."""
    symbol = str(symbol).strip().upper()
    if symbol not in STOCK_PRICES:
        return False, f"{symbol or 'That symbol'} is not in the price list."
    if quantity is None or quantity <= 0:
        return False, "Quantity must be 1 or more."
    holdings[symbol] = holdings.get(symbol, 0) + int(quantity)
    return True, f"Added {int(quantity)} x {symbol} to your portfolio"


def set_quantity(holdings, symbol, quantity):
    """Replace the quantity of an existing stock."""
    if symbol in holdings and quantity and quantity > 0:
        holdings[symbol] = int(quantity)


def remove_stock(holdings, symbol):
    holdings.pop(symbol, None)


def to_dataframe(holdings):
    """Turn the dictionary into a table with price, investment and share %."""
    rows = []
    for symbol, qty in holdings.items():
        price = STOCK_PRICES[symbol]
        rows.append({"Symbol": symbol, "Name": STOCK_NAMES[symbol],
                     "Quantity": qty, "Price": price, "Investment": qty * price})
    df = pd.DataFrame(rows, columns=COLUMNS)
    total = df["Investment"].sum()
    df["Share"] = (df["Investment"] / total * 100) if total > 0 else 0.0
    return df.sort_values("Investment", ascending=False).reset_index(drop=True)


def overview(df):
    """Numbers for the four overview cards."""
    if df.empty:
        return {"total": 0, "count": 0, "quantity": 0, "top": "-"}
    return {"total": int(df["Investment"].sum()), "count": len(df),
            "quantity": int(df["Quantity"].sum()), "top": df.iloc[0]["Symbol"]}


def diversification(df):
    """0% = everything in one stock, 100% = perfectly even split."""
    if len(df) < 2:
        return 0.0
    shares = df["Share"] / 100
    concentration = (shares ** 2).sum()
    return round((1 - concentration) / (1 - 1 / len(df)) * 100, 1)


def summary_text(df):
    """Plain-text summary used for the TXT download."""
    if df.empty:
        return "StockHolmes portfolio summary\nYour portfolio is empty.\n"
    info = overview(df)
    lines = ["StockHolmes portfolio summary", "=" * 28, ""]
    for _, r in df.iterrows():
        lines.append(f"{r.Symbol:<6} {r.Quantity:>5} x ${r.Price:<5} = ${r.Investment:>8,.0f}  ({r.Share:.1f}%)")
    lines += ["", f"Total investment : ${info['total']:,}",
              f"Stocks held      : {info['count']}",
              f"Total quantity   : {info['quantity']}",
              f"Diversification  : {diversification(df)}%",
              "", "Prices are fixed demo values, not live market data."]
    return "\n".join(lines)