# Quiet Ledger

A Flask portfolio-tracker built as a training project.

## What this is

- "Quiet Ledger" -- a dashboard showing a portfolio (dummy seed data, not
  real market data) with a net worth chart, an allocation donut, and
  simple add/delete CRUD for holdings and transactions.
- No real login/auth. One hardcoded `DUMMY_USER_ID = 1` in `quiet_app.py`.
  Every `sql.py` function takes a `user_id` param on purpose, so real auth
  could later swap in "whoever is logged in" without touching anything else.
- Goal throughout: code the owner can read, understand, and explain --
  favor fewer features and plain code over abstraction.

## How to run

```
python -m venv venv
venv\Scripts\Activate.ps1      # Windows
pip install -r requirements.txt
python quiet_app.py            # http://127.0.0.1:4000
```

The News page pulls headlines from the Finnhub API. `finnhub_key.py` ships
with an empty key so the app runs out of the box (News will just show no
articles); drop in a free key from https://finnhub.io/register to see it
work.

## Files

- `quiet_app.py` -- Flask app, all routes, all view logic.
- `sql.py` -- plain-function SQLite data layer (not Flask's `g` pattern).
  Money is stored as INTEGER cents everywhere (never REAL/float) to avoid
  rounding errors. `quantity` is REAL (fractional shares are real, e.g.
  11.5 shares). `DB_PATH` is anchored to this file's own directory via
  `__file__`, not a relative path -- a relative `sqlite3.connect('quiet.db')`
  silently creates a second empty DB depending on which directory you
  launch python from.
- `charts.py` -- the only file that imports matplotlib. Renders the net
  worth line chart to a PNG (`matplotlib.use("Agg")`, no GUI backend).
  The allocation donut is NOT here -- it's plain SVG built in
  `dashboard.html` directly from each holding's percentage, so each wedge
  can carry a native `<title>` hover tooltip with zero JavaScript.
- `news.py` -- fetches recent headlines per holding symbol from the
  Finnhub API.
- `templates/` -- `base.html` (shared layout/sidebar/topbar/dark-mode
  toggle), `dashboard.html`, `holdings.html`, `transactions.html`, `news.html`.
- `static/style.css` -- one file, CSS custom properties in `:root` /
  `:root.dark` so the whole theme (light/dark, accent color) changes from
  one place.
- `requirements.txt` -- flask, matplotlib, requests.

## Notable decisions / gotchas

- Dark mode: `localStorage` + a `.dark` class toggled on `<html>`, no
  server involvement.
- `/holdings/add` and `/transactions/add` wrap the form parsing in
  try/except -- blank or non-numeric input skips the insert instead of
  crashing with a raw 500 page.
- The net-worth chart is a simulated random walk (seeded, so it's stable
  across reloads) ending at today's real computed total value -- there's
  no real historical snapshots table.
- Chart PNGs are rendered at `dpi=150` (not matplotlib's default 100) so
  the card looks sharp when it stretches wide on a big monitor.

