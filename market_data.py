"""market_data.py - simulated price history for the market charts.

There is no live feed here. Each stock gets a repeatable random walk that ends
exactly at its price in stock_data.py, so the same symbol always draws the same chart.
"""
import numpy as np
import pandas as pd
from stock_data import STOCK_PRICES

DAYS = 180
_cache = {}


def history(symbol):
    """Open, High, Low, Close, Volume plus SMA, Bollinger bands and RSI."""
    if symbol in _cache:
        return _cache[symbol]
    rng = np.random.default_rng(sum(ord(c) for c in symbol) * 7919)
    rets = rng.normal(0.0005, 0.017, DAYS)
    close = STOCK_PRICES[symbol] * np.exp(np.cumsum(rets) - rets.sum())  # last close = listed price
    open_ = np.concatenate([[close[0]], close[:-1]]) * (1 + rng.normal(0, 0.003, DAYS))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.006, DAYS)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.006, DAYS)))
    volume = (rng.integers(20, 60, DAYS) * 1e5 * (1 + np.abs(rets) * 40)).astype(int)
    df = pd.DataFrame({"Date": pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=DAYS),
                       "Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume})
    df["SMA20"] = df.Close.rolling(20).mean()
    df["SMA50"] = df.Close.rolling(50).mean()
    std = df.Close.rolling(20).std()
    df["BBU"] = df.SMA20 + 2 * std
    df["BBL"] = df.SMA20 - 2 * std
    delta = df.Close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    df["RSI"] = 100 - 100 / (1 + gain / loss)
    _cache[symbol] = df
    return df


def day_change(symbol):
    """Simulated change of the last day, in percent."""
    c = history(symbol).Close
    return (c.iloc[-1] / c.iloc[-2] - 1) * 100


def sparkline(symbol, n=30):
    """Tiny inline SVG trend line; green if up over the period, coral if down."""
    c = history(symbol).Close.tail(n).to_numpy()
    lo, hi = c.min(), c.max()
    pts = " ".join(f"{i * 80 / (n - 1):.1f},{24 - (v - lo) / (hi - lo + 1e-9) * 22:.1f}" for i, v in enumerate(c))
    color = "#39FFA0" if c[-1] >= c[0] else "#FF6B8A"
    return (f'<svg class="spark" width="80" height="26" viewBox="0 0 80 26"><polyline points="{pts}" '
            f'fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round"/></svg>')


def portfolio_curve(holdings, days=90):
    """Value of the whole portfolio over time (quantity x simulated close)."""
    total = None
    for symbol, qty in holdings.items():
        part = history(symbol).set_index("Date").Close.tail(days) * qty
        total = part if total is None else total + part
    return total