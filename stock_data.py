"""stock_data.py - the hardcoded price list (no paid API needed)."""

# Prices are fixed demo values, NOT live market prices.
STOCK_PRICES = {
    "AAPL": 180,
    "TSLA": 250,
    "GOOGL": 140,
    "MSFT": 420,
    "AMZN": 190,
    "NVDA": 135,
}

# Company names shown next to the symbols.
STOCK_NAMES = {
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla Inc.",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft Corp.",
    "AMZN": "Amazon.com Inc.",
    "NVDA": "NVIDIA Corp.",
}

# Used by the "Load sample portfolio" button.
SAMPLE_PORTFOLIO = {"AAPL": 15, "MSFT": 6, "NVDA": 30, "TSLA": 8, "GOOGL": 12}