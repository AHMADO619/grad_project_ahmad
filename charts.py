# Renders the dashboard chart PNGs net worth line and pie chart
import io
from datetime import date
import matplotlib
from matplotlib.figure import Figure

# the app only saves PNG files to use on the page
matplotlib.use("Agg")

# How many days back each range button shows.
RANGE_DAYS = {"3m": 90, "6m": 180, "1y": 365}

# color data for pie chart
PALETTE = ["#2dd4a0", "#60a5fa", "#f59e0b", "#f87171", "#a78bfa", "#22d3ee", "#f472b6"]

# net worth line chart
def net_worth_chart_png(history_rows):
    dates = []
    values = []
    for row in history_rows:
        dates.append(date.fromisoformat(row['date']))
        values.append(row['value_cents'] / 100)

    fig = Figure(figsize=(7, 4.54))
    ax = fig.add_subplot(111)

    ax.set_facecolor("none")
    ax.plot(dates, values, color="#2dd4a0")
    ax.set_title("Net worth over time", color="#cccccc")
    ax.set_ylabel("Value ($)", color="#cccccc")
    fig.autofmt_xdate(rotation=30, ha="right")
    ax.tick_params(color="#4b4b4f", labelcolor="#cccccc")
    for spine in ax.spines.values():
        spine.set_color("#4b4b4f")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True, dpi=150)
    buf.seek(0)
    return buf.read()

# Used by quiet_app.py to size the pie chart hover ring 
DONUT_HOVER_CIRCUMFERENCE = 56.5

# pie chart directly from data
def allocation_chart_png(holdings):
    values = []
    colors = []
    i = 0
    for h in holdings:
        values.append(h['quantity'] * h['current_price'])
        colors.append(PALETTE[i % len(PALETTE)])
        i += 1

    fig = Figure(figsize=(4.6, 4.6))
    ax = fig.add_subplot(111)
    ax.pie(values, colors=colors, wedgeprops={"width": 0.4}, startangle=90, counterclock=False)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True, dpi=150)
    buf.seek(0)
    return buf.read()
