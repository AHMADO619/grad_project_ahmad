from datetime import date
from flask import Flask, render_template, request, redirect, url_for, Response
import sql
import charts
import news

app = Flask(__name__, template_folder='templates')
# fake user account
DUMMY_USER_ID = 1

# function to turn a dollar string from a form (like "24.50") into cents
def parse_price_cents(form, field_name):
    return round(float(form[field_name]) * 100)

# money formatting to turn an integer cents value into a dollar string
@app.template_filter("money")
def format_money(cents):
    cents = cents or 0
    sign = "-" if cents < 0 else ""
    return f"{sign}${abs(cents) / 100:,.2f}"

# example 24.0 -> "24", 11.5 -> "11.5"
@app.template_filter("qty")
def format_qty(quantity):
    return f"{quantity:g}"

# function to send people straight to the dashboard
@app.route('/')
def home():
    return redirect(url_for('dashboard'))

# holdings
@app.route('/holdings')
def holdings():
    rows = sql.holdings_by_user_id(DUMMY_USER_ID)
    return render_template('holdings.html', holdings=rows)

# function to add a new holding from the form on the holdings page
@app.route('/holdings/add', methods=['POST'])
def add_holding_route():
    try:
        purchase_price = parse_price_cents(request.form, 'purchase_price')
        holding = {
            'user_id': DUMMY_USER_ID,
            'symbol': request.form['symbol'].upper().strip(),
            'quantity': float(request.form['quantity']),
            'purchase_price': purchase_price,
            'current_price': purchase_price,
        }
        sql.add_holding(holding)
    except (ValueError, KeyError):
        pass
    return redirect(url_for('holdings'))

# function to delete one holding by id
@app.route('/holdings/<int:holding_id>/delete', methods=['POST'])
def delete_holding_route(holding_id):
    sql.delete_holding(holding_id)
    return redirect(url_for('holdings'))

# transactions
@app.route('/transactions')
def transactions():
    rows = sql.get_all_transactions()
    return render_template('transactions.html', transactions=rows)

# function to add a new transaction from the form on the transactions page
@app.route('/transactions/add', methods=['POST'])
def add_transaction_route():
    try:
        sale_price = parse_price_cents(request.form, 'sale_price') if request.form.get('sale_price') else None
        sale_date = request.form.get('sale_date') or None

        transaction = {
            'user_id': DUMMY_USER_ID,
            'symbol': request.form['symbol'].upper().strip(),
            'quantity': float(request.form['quantity']),
            'purchase_price': parse_price_cents(request.form, 'purchase_price'),
            'sale_price': sale_price,
            'sale_date': sale_date,
        }
        sql.add_transaction(transaction)
    except (ValueError, KeyError):
        pass
    return redirect(url_for('transactions'))

# function to delete one transaction by id
@app.route('/transactions/<int:transaction_id>/delete', methods=['POST'])
def delete_transaction_route(transaction_id):
    sql.delete_transaction(transaction_id)
    return redirect(url_for('transactions'))

# dashboard
@app.route('/dashboard')
def dashboard():
    rows = sql.holdings_by_user_id(DUMMY_USER_ID)

    cost_basis_cents = 0
    total_value_cents = 0
    for row in rows:
        cost_basis_cents += row['quantity'] * row['purchase_price']
        total_value_cents += row['quantity'] * row['current_price']
    total_return_cents = total_value_cents - cost_basis_cents
    if cost_basis_cents:
        total_return_pct = total_return_cents / cost_basis_cents * 100
    else:
        total_return_pct = 0

    holdings_view = []

    i = 0
    
    # start at 12 o'clock
    dash_offset = charts.DONUT_HOVER_CIRCUMFERENCE * 0.25  
    for row in rows:
        value_cents = row['quantity'] * row['current_price']
        cost_cents = row['quantity'] * row['purchase_price']
        return_cents = value_cents - cost_cents
        if cost_cents:
            return_pct = return_cents / cost_cents * 100
        else:
            return_pct = 0
        if total_value_cents:
            allocation_pct = value_cents / total_value_cents * 100
        else:
            allocation_pct = 0
        color_index = i % len(charts.PALETTE)  # wraps around once colors run out
        dash_length = allocation_pct / 100 * charts.DONUT_HOVER_CIRCUMFERENCE
        holdings_view.append({
            'symbol': row['symbol'],
            'quantity': row['quantity'],
            'current_price': row['current_price'],
            'value_cents': value_cents,
            'return_cents': return_cents,
            'return_pct': return_pct,
            'allocation_pct': allocation_pct,
            'color': charts.PALETTE[color_index],
            'dash_length': dash_length,
            'dash_gap': charts.DONUT_HOVER_CIRCUMFERENCE - dash_length,
            'dash_offset': dash_offset,
        })
        dash_offset -= dash_length
        i += 1

    chart_range = request.args.get('range', '1y')
    if chart_range not in charts.RANGE_DAYS:
        chart_range = '1y'

    return render_template(
        'dashboard.html',
        holdings=holdings_view,
        today_str=date.today().strftime('%A, %B %d, %Y'),
        cost_basis_cents=cost_basis_cents,
        total_value_cents=total_value_cents,
        total_return_cents=total_return_cents,
        total_return_pct=total_return_pct,
        chart_range=chart_range,
    )

# chart images (Matplotlib)
@app.route('/charts/net-worth.png')
def net_worth_chart():
    chart_range = request.args.get('range', '1y')
    if chart_range not in charts.RANGE_DAYS:
        chart_range = '1y'
    days = charts.RANGE_DAYS[chart_range]

    rows = sql.net_worth_history_by_user_id(DUMMY_USER_ID, days)
    png = charts.net_worth_chart_png(rows)
    # no-store so the browser always asks the server for a fresh chart to fix a bug i had
    response = Response(png, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store'
    return response

# function to serve the allocation pie chart as a PNG
@app.route('/charts/allocation.png')
def allocation_chart():
    rows = sql.holdings_by_user_id(DUMMY_USER_ID)
    png = charts.allocation_chart_png(rows)
    response = Response(png, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store'
    return response

# function to show recent news for each holding
@app.route('/news')
def news_page():
    rows = sql.holdings_by_user_id(DUMMY_USER_ID)

    news_view = []
    for row in rows:
        articles = news.get_news_for_symbol(row['symbol'])
        news_view.append({
            'symbol': row['symbol'],
            'articles': articles,
        })

    return render_template('news.html', news_view=news_view)

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=4000)
