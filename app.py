"""app.py - the StockHolmes interface. Run with: streamlit run app.py"""
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import market_data as md
import portfolio as pf
from stock_data import STOCK_PRICES, STOCK_NAMES, SAMPLE_PORTFOLIO

st.set_page_config(page_title="StockHolmes", page_icon="🔍", layout="wide")

# ---------- Load custom CSS ----------
BASE = Path(__file__).parent
st.markdown(f"<style>{(BASE / 'styles.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ---------- Session state: the portfolio lives here ----------
if "holdings" not in st.session_state:
    st.session_state.holdings = {}
holdings = st.session_state.holdings

# Show a toast left over from the previous action (survives st.rerun)
if "flash" in st.session_state:
    st.toast(st.session_state.pop("flash"), icon="✅")

PALETTE = ["#39FFA0", "#8B7CFF", "#4CC9F0", "#FFC857", "#FF6B8A", "#B8F28B"]
COLORS = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(STOCK_PRICES)}

ICONS = {
    "wallet": '<path d="M3 7h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7zm0 0 2-3h12"/><circle cx="16.5" cy="13.5" r="1.2"/>',
    "layers": '<path d="m12 3 9 5-9 5-9-5 9-5zM3 12l9 5 9-5M3 16l9 5 9-5"/>',
    "hash": '<path d="M4 8h16M4 16h16M9 3 7 21M17 3l-2 18"/>',
    "star": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9L12 3z"/>',
}


def icon(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


def money(x):
    return f"${x:,.0f}"


def style(fig, height):
    """Shared dark chart look."""
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=height,
                      font=dict(color="#E8EEF8", family="Figtree"), margin=dict(t=20, b=10, l=10, r=10),
                      hoverlabel=dict(bgcolor="#0B1322", bordercolor="#39FFA0"))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,.06)")
    return fig


def clear_qty_keys():
    """Forget old quantity inputs so they pick up fresh values."""
    for key in [k for k in st.session_state if k.startswith("qty_")]:
        del st.session_state[key]


# ---------- Button callbacks ----------
def load_sample():
    clear_qty_keys()
    st.session_state.holdings = dict(SAMPLE_PORTFOLIO)
    st.session_state.flash = "Sample portfolio loaded"


def change_qty(symbol):
    pf.set_quantity(st.session_state.holdings, symbol, st.session_state[f"qty_{symbol}"])


def save_to_disk(df):
    (BASE / "assets").mkdir(exist_ok=True)
    df.to_csv(BASE / "assets" / "portfolio.csv", index=False)
    (BASE / "assets" / "portfolio_summary.txt").write_text(pf.summary_text(df), encoding="utf-8")
    st.session_state.flash = "Saved to the assets folder"


# ---------- Confirmation dialogs ----------
@st.dialog("Remove this stock?")
def confirm_remove(symbol):
    st.write(f"**{symbol}** will be removed from your portfolio.")
    a, b = st.columns(2)
    if a.button("Remove", type="primary", key="do_remove"):
        pf.remove_stock(holdings, symbol)
        clear_qty_keys()
        st.session_state.flash = f"Removed {symbol}"
        st.rerun()
    if b.button("Keep it", key="keep"):
        st.rerun()


@st.dialog("Reset portfolio?")
def confirm_reset():
    st.write("This clears every stock you added.")
    a, b = st.columns(2)
    if a.button("Reset", type="primary", key="do_reset"):
        holdings.clear()
        clear_qty_keys()
        st.session_state.flash = "Portfolio reset"
        st.rerun()
    if b.button("Cancel", key="cancel_reset"):
        st.rerun()


@st.dialog("Stock details")
def show_details(row):
    st.markdown(f"### {row.Symbol} · {row.Name}")
    c1, c2 = st.columns(2)
    c1.metric("Price per share", money(row.Price))
    c2.metric("Quantity", row.Quantity)
    c1.metric("Total investment", money(row.Investment))
    c2.metric("Share of portfolio", f"{row.Share:.1f}%")


# ---------- Data for this run ----------
df = pf.to_dataframe(holdings)
info = pf.overview(df)

# ---------- Ticker tape ----------
items = "".join(f"<span><b>{s}</b>${p}</span>" for s, p in STOCK_PRICES.items())
st.markdown(f'<div class="tape"><div class="tape-track">{items}{items}</div></div>', unsafe_allow_html=True)

# ---------- Hero ----------
if df.empty:
    ribbon = '<div class="ribbon-empty">Your allocation will draw itself here once you add a stock</div>'
    headline = "Welcome to StockHolmes. Let's open your first case."
    big = "$0"
else:
    segs = "".join(
        f'<div class="seg" style="flex:{r.Share};background:{COLORS[r.Symbol]}" '
        f'title="{r.Symbol}: {r.Share:.1f}%">{r.Symbol}</div>' for r in df.itertuples())
    ribbon = f'<div class="ribbon">{segs}</div>'
    headline = "Welcome back. Here is where your money sits."
    big = money(info["total"])

logo = ('<svg viewBox="0 0 34 34"><circle cx="14" cy="14" r="10" fill="none" stroke="#39FFA0" stroke-width="3"/>'
        '<path d="M22 22l9 9" stroke="#39FFA0" stroke-width="4" stroke-linecap="round"/>'
        '<rect x="8" y="14" width="3" height="6" rx="1" fill="#39FFA0" opacity=".6"/>'
        '<rect x="13" y="8" width="3" height="12" rx="1" fill="#39FFA0"/>'
        '<rect x="18" y="11" width="3" height="9" rx="1" fill="#39FFA0" opacity=".8"/></svg>')
st.markdown(
    f'<div class="hero"><div class="brand">{logo}StockHolmes<small>Track your investments. '
    f'Visualize your growth. Own your financial journey.</small></div>'
    f'<h1>{headline}</h1><div class="total">{big}</div>'
    f'<div class="sub">Total invested across {info["count"]} stock(s), priced from your own list. '
    f'Each block below is one stock, sized by its share.</div>{ribbon}</div>',
    unsafe_allow_html=True)

tab_over, tab_mkt, tab_add, tab_hold, tab_ins, tab_exp = st.tabs(
    ["Overview", "Markets", "Add stock", "My portfolio", "Insights", "Export"])

# ================= OVERVIEW =================
with tab_over:
    cards = [("wallet", money(info["total"]), "Total investment"),
             ("layers", info["count"], "Stocks held"),
             ("hash", f'{info["quantity"]:,}', "Total shares"),
             ("star", info["top"], "Biggest position")]
    html = "".join(f'<div class="glass stat"><div class="ic">{icon(i)}</div>'
                   f'<div class="num">{n}</div><div class="lbl">{l}</div></div>' for i, n, l in cards)
    st.markdown(f'<div class="grid4">{html}</div>', unsafe_allow_html=True)

    if df.empty:
        st.markdown('<div class="glass empty"><div class="orb"></div><h3>Nothing here yet</h3>'
                    '<p class="mute">Add your first stock, or load a sample to see StockHolmes in action.</p></div>',
                    unsafe_allow_html=True)
        st.button("Load sample portfolio", type="primary", on_click=load_sample)
    else:
        colors = [COLORS[s] for s in df.Symbol]
        left, right = st.columns(2)
        donut = go.Figure(go.Pie(
            labels=df.Symbol, values=df.Investment, hole=0.68, sort=False,
            marker=dict(colors=colors, line=dict(color="#060A12", width=3)),
            hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>"))
        donut.update_layout(annotations=[dict(text=f"<b>{money(info['total'])}</b>", showarrow=False,
                                              font=dict(size=22, color="#E8EEF8"))])
        bars = go.Figure(go.Bar(
            x=df.Symbol, y=df.Investment, marker=dict(color=colors, cornerradius=8),
            hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"))
        bars.update_yaxes(gridcolor="rgba(255,255,255,.07)", tickprefix="$")
        for fig, col, title in ((donut, left, "Where it is invested"), (bars, right, "Investment per stock")):
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=340,
                              font=dict(color="#E8EEF8", family="Figtree"), margin=dict(t=10, b=10, l=10, r=10),
                              showlegend=False, hoverlabel=dict(bgcolor="#0B1322", bordercolor="#39FFA0"))
            with col:
                st.markdown(f"### {title}")
                st.plotly_chart(fig, config={"displayModeBar": False})

        curve = md.portfolio_curve(holdings)
        area = go.Figure(go.Scatter(
            x=curve.index, y=curve.values, mode="lines", line=dict(color="#39FFA0", width=2.6),
            fill="tozeroy", fillcolor="rgba(57,255,160,.13)",
            hovertemplate="%{x|%d %b}<br><b>$%{y:,.0f}</b><extra></extra>"))
        style(area, 300)
        area.update_yaxes(tickprefix="$", range=[curve.min() * 0.97, curve.max() * 1.02])
        st.markdown("### Portfolio value over 90 days")
        st.markdown('<span class="demo">Simulated demo history, not live market data</span>', unsafe_allow_html=True)
        st.plotly_chart(area, config={"displayModeBar": False})

# ================= MARKETS =================
with tab_mkt:
    st.markdown("### Market lab")
    st.markdown('<span class="demo">Simulated demo history, not live market data</span>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns([1.3, 1, 1.2])
    sym = m1.selectbox("Stock", list(STOCK_PRICES), key="mkt_sym", format_func=lambda s: f"{s} · {STOCK_NAMES[s]}")
    kind = m2.radio("Chart type", ["Candles", "Line", "Area"], horizontal=True)
    days = m3.select_slider("Range in days", options=[30, 60, 90, 180], value=90)
    o1, o2, o3 = st.columns(3)
    show_sma = o1.checkbox("Moving averages", value=True)
    show_bb = o2.checkbox("Bollinger bands")
    show_rsi = o3.checkbox("RSI panel", value=True)

    h = md.history(sym).tail(days)
    change = (h.Close.iloc[-1] / h.Close.iloc[0] - 1) * 100
    cells = [("Last price", f"${h.Close.iloc[-1]:,.2f}"), (f"{days}-day change", f"{change:+.1f}%"),
             ("Period high", f"${h.High.max():,.2f}"), ("Period low", f"${h.Low.min():,.2f}")]
    st.markdown('<div class="grid4">' + "".join(
        f'<div class="glass stat"><div class="num">{v}</div><div class="lbl">{k}</div></div>' for k, v in cells)
        + '</div>', unsafe_allow_html=True)

    rows = 3 if show_rsi else 2
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        row_heights=[0.6, 0.17, 0.23] if show_rsi else [0.78, 0.22])
    # Row 1: price (candlesticks, line or area)
    if kind == "Candles":
        fig.add_trace(go.Candlestick(
            x=h.Date, open=h.Open, high=h.High, low=h.Low, close=h.Close, name=sym,
            increasing_line_color="#39FFA0", increasing_fillcolor="#39FFA0",
            decreasing_line_color="#FF6B8A", decreasing_fillcolor="#FF6B8A"), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=h.Date, y=h.Close, name=sym, line=dict(color="#39FFA0", width=2.4),
            fill="tozeroy" if kind == "Area" else None, fillcolor="rgba(57,255,160,.12)"), row=1, col=1)
    if show_sma:
        fig.add_trace(go.Scatter(x=h.Date, y=h.SMA20, name="SMA 20", line=dict(color="#FFC857", width=1.4)), row=1, col=1)
        fig.add_trace(go.Scatter(x=h.Date, y=h.SMA50, name="SMA 50", line=dict(color="#4CC9F0", width=1.4)), row=1, col=1)
    if show_bb:
        band = dict(color="rgba(139,124,255,.65)", width=1)
        fig.add_trace(go.Scatter(x=h.Date, y=h.BBU, name="Upper band", line=band), row=1, col=1)
        fig.add_trace(go.Scatter(x=h.Date, y=h.BBL, name="Lower band", line=band,
                                 fill="tonexty", fillcolor="rgba(139,124,255,.10)"), row=1, col=1)
    # Row 2: volume bars, green on up days and coral on down days
    fig.add_trace(go.Bar(x=h.Date, y=h.Volume, name="Volume", marker_color=[
        "rgba(57,255,160,.55)" if up else "rgba(255,107,138,.55)" for up in (h.Close >= h.Open)]), row=2, col=1)
    # Row 3: RSI with the usual 30 / 70 guide lines
    if show_rsi:
        fig.add_trace(go.Scatter(x=h.Date, y=h.RSI, name="RSI 14", line=dict(color="#8B7CFF", width=1.8)), row=3, col=1)
        for level in (30, 70):
            fig.add_hline(y=level, line=dict(color="rgba(255,255,255,.25)", dash="dot", width=1), row=3, col=1)
        fig.update_yaxes(range=[0, 100], row=3, col=1)
    style(fig, 640)
    fig.update_layout(hovermode="x unified", xaxis_rangeslider_visible=False,
                      legend=dict(orientation="h", y=1.04, x=0))
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    fig.update_yaxes(range=[h.Low.min() * 0.98, h.High.max() * 1.02], row=1, col=1)
    st.plotly_chart(fig, config={"displayModeBar": False})

    # Heatmap and comparison, the two classic market overview charts
    moves = {s: md.day_change(s) for s in STOCK_PRICES}
    tree = go.Figure(go.Treemap(
        labels=list(moves), parents=[""] * len(moves), values=[1] * len(moves),
        customdata=[[v, STOCK_PRICES[s]] for s, v in moves.items()],
        texttemplate="<b>%{label}</b><br>%{customdata[0]:+.2f}%",
        hovertemplate="<b>%{label}</b><br>$%{customdata[1]}<br>%{customdata[0]:+.2f}% (simulated)<extra></extra>",
        marker=dict(colors=list(moves.values()), cmid=0, line=dict(width=3, color="#060A12"),
                    colorscale=[[0, "#C2415C"], [0.5, "#1B2436"], [1, "#1FB57A"]]),
        textfont=dict(size=20, color="#FFFFFF")))
    cmp = go.Figure()
    for s in STOCK_PRICES:
        d = md.history(s).tail(days)
        cmp.add_trace(go.Scatter(x=d.Date, y=d.Close / d.Close.iloc[0] * 100, name=s,
                                 line=dict(color=COLORS[s], width=2)))
    cmp.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.12, x=0))
    cmp.update_yaxes(ticksuffix="%")
    h1, h2 = st.columns(2)
    with h1:
        st.markdown("### Market heatmap")
        st.plotly_chart(style(tree, 340), config={"displayModeBar": False})
    with h2:
        st.markdown("### Compare stocks, starting at 100")
        st.plotly_chart(style(cmp, 340), config={"displayModeBar": False})

# ================= ADD STOCK =================
with tab_add:
    st.markdown("### Add a stock")
    c1, c2 = st.columns(2)
    symbol = c1.selectbox("Stock symbol", list(STOCK_PRICES), format_func=lambda s: f"{s} · {STOCK_NAMES[s]}")
    qty = c2.number_input("Quantity", min_value=1, value=1, step=1)
    price = STOCK_PRICES[symbol]
    st.markdown(f'<div class="glass" style="margin:.8rem 0 1rem"><span class="mute">{qty} x ${price} per share</span>'
                f'<div class="quote">{money(qty * price)}</div></div>', unsafe_allow_html=True)
    if st.button("Add to portfolio", type="primary"):
        ok, msg = pf.add_stock(holdings, symbol, qty)
        if ok:
            clear_qty_keys()
            st.session_state.flash = msg
            st.rerun()
        else:
            st.error(msg)

# ================= MY PORTFOLIO =================
with tab_hold:
    if df.empty:
        st.markdown('<div class="glass empty"><div class="orb"></div><h3>No holdings yet</h3>'
                    '<p class="mute">Head to "Add stock" to get started.</p></div>', unsafe_allow_html=True)
    else:
        rows = "".join(
            f'<tr><td><span class="dot" style="background:{COLORS[r.Symbol]}"></span>'
            f'<span class="sym">{r.Symbol}</span><span class="nm">{r.Name}</span></td>'
            f'<td>{r.Quantity}</td><td>${r.Price}</td><td>{money(r.Investment)}</td>'
            f'<td><span class="bar"><i style="width:{r.Share:.0f}%;background:{COLORS[r.Symbol]}"></i></span>'
            f'{r.Share:.1f}%</td><td>{md.sparkline(r.Symbol)}</td></tr>' for r in df.itertuples())
        st.markdown('<div class="glass tbl-wrap"><table class="tbl"><tr><th>Stock</th><th>Quantity</th>'
                    f'<th>Price per share</th><th>Total investment</th><th>Portfolio share</th><th>30-day trend</th></tr>{rows}</table></div>',
                    unsafe_allow_html=True)

        st.markdown("### Manage a holding")
        pick = st.selectbox("Choose a stock", list(df.Symbol), key="manage_pick")
        st.number_input("Edit quantity (updates instantly)", min_value=1, step=1,
                        value=int(holdings[pick]), key=f"qty_{pick}",
                        on_change=change_qty, args=(pick,))
        b1, b2, b3 = st.columns(3)
        if b1.button("View details"):
            show_details(df[df.Symbol == pick].iloc[0])
        if b2.button("Remove stock"):
            confirm_remove(pick)
        if b3.button("Reset portfolio"):
            confirm_reset()

# ================= INSIGHTS =================
with tab_ins:
    if df.empty:
        st.markdown('<div class="glass empty"><div class="orb"></div><h3>Insights appear here</h3>'
                    '<p class="mute">Add a few stocks and StockHolmes will summarise them.</p></div>', unsafe_allow_html=True)
    else:
        high, low = df.iloc[0], df.iloc[-1]
        most = df.sort_values("Quantity", ascending=False).iloc[0]
        div = pf.diversification(df)
        items = [("Highest investment", high.Symbol, money(high.Investment)),
                 ("Lowest investment", low.Symbol, money(low.Investment)),
                 ("Most shares owned", most.Symbol, f"{most.Quantity} shares"),
                 ("Diversification", f"{div}%", "how evenly money is spread")]
        html = "".join(f'<div class="glass stat"><div class="lbl">{a}</div><div class="num">{b}</div>'
                       f'<div class="lbl">{c}</div></div>' for a, b, c in items)
        st.markdown(f'<div class="grid4">{html}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="glass"><b>Summary.</b> You hold {info["count"]} stock(s) with {info["quantity"]} shares, '
            f'worth {money(info["total"])} at your listed prices. {high.Symbol} is your largest position at '
            f'{high.Share:.1f}% of the portfolio.</div>'
            '<div class="note">Prices are fixed demo values, so StockHolmes does not show market performance or profit and loss.</div>',
            unsafe_allow_html=True)

# ================= EXPORT =================
with tab_exp:
    st.markdown("### Export your portfolio")
    if df.empty:
        st.info("Add a stock first. Exports need at least one holding.")
    else:
        e1, e2, e3 = st.columns(3)
        e1.download_button("Download CSV", df.to_csv(index=False), "stockholmes_portfolio.csv", "text/csv")
        e2.download_button("Download TXT", pf.summary_text(df), "stockholmes_portfolio.txt", "text/plain")
        e3.button("Save summary to disk", on_click=save_to_disk, args=(df,))
        st.code(pf.summary_text(df), language=None)