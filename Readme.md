# StockHolmes – Smart Portfolio Tracker
*Track your investments. Visualize your growth. Own your financial journey.*

A dark, glassmorphism fintech dashboard built with Python and Streamlit. Prices come from a hardcoded dictionary, so no paid API is needed.

## Features
- Add stocks from a dropdown with live cost preview
- Allocation ribbon, donut chart and bar chart that update instantly
- Edit quantity, remove stocks (with confirmation), view details, reset
- Insights: highest, lowest, most shares, diversification
- Export to CSV or TXT, plus save to `assets/`
- Market lab: candlestick, line and area charts, moving averages, Bollinger bands, volume, RSI, heatmap and comparison (simulated demo data)
- Sample portfolio, empty states, toast notifications, responsive layout

## Tech
Python, Streamlit, Pandas, Plotly, custom CSS

## Install and run (Windows PowerShell)
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Structure
```
stockholmes/
├── app.py          # interface and layout
├── stock_data.py   # price list and sample portfolio
├── market_data.py  # simulated price history and indicators
├── portfolio.py    # calculations and data handling
├── styles.css      # all custom styling
├── requirements.txt
└── assets/         # saved exports and screenshots
```

## Screenshots
Add images to `assets/` and link them here.

## Future improvements
Live price API, multiple portfolios, user accounts, price history charts.

Prices are fixed demo values, not live market data.