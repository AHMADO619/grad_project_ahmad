# adding libraries and connecting to the database
import os
import sqlite3

# database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quiet.db')

# function to open a connection to the database
def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# creating tables for the database
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, symbol TEXT, quantity REAL, purchase_price INTEGER, sale_price INTEGER, sale_date TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS holdings (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, symbol TEXT, quantity REAL, purchase_price INTEGER, current_price INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS net_worth_history (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, date TEXT, value_cents INTEGER)''')
    conn.commit()
    conn.close()

# add demo data
def seed_dummy_data(user_id=1):
    conn = connect_db()
    cursor = conn.cursor()
    existing = cursor.execute('SELECT COUNT(*) AS n FROM holdings WHERE user_id = ?', (user_id,)).fetchone()
    if existing['n'] > 0:
        conn.close()
        return

    # (symbol, quantity, purchase_price cents, current_price cents)
    dummy_holdings = [
        ('AAPL', 24, 15872, 23214),
        ('BND', 62, 7128, 7396),
        ('CASH', 1, 860000, 860000),
        ('MSFT', 11.5, 28640, 50677),
        ('VOO', 38.4, 40218, 52142),
        ('VXUS', 47, 5584, 6831),
    ]
    for symbol, quantity, purchase_price, current_price in dummy_holdings:
        cursor.execute(
            'INSERT INTO holdings (user_id, symbol, quantity, purchase_price, current_price) VALUES (?, ?, ?, ?, ?)',
            (user_id, symbol, quantity, purchase_price, current_price),
        )
    conn.commit()
    conn.close()

# function to get a users net worth history for the line chart
def net_worth_history_by_user_id(user_id, days=365):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM net_worth_history WHERE user_id = ? ORDER BY date DESC LIMIT ?',
        (user_id, days + 1),
    )
    rows = cursor.fetchall()
    conn.close()
    # oldest -> newest
    rows.reverse()  
    return rows

# adding holdings to the database and crud operations for holdings
def add_holding(holding):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO holdings (user_id, symbol, quantity, purchase_price, current_price) VALUES (?, ?, ?, ?, ?)',
        (holding['user_id'], holding['symbol'], holding['quantity'], holding['purchase_price'], holding['current_price']),
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid

# function to get users holdings from the database
def holdings_by_user_id(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM holdings WHERE user_id = ?', (user_id,))
    holdings = cursor.fetchall()
    conn.close()
    return holdings

# function to delete one holding by id
def delete_holding(holding_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM holdings WHERE id = ?', (holding_id,))
    conn.commit()
    conn.close()

# adding transactions to the database and crud operations for transactions
def add_transaction(transaction):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO transactions (user_id, symbol, quantity, purchase_price, sale_price, sale_date) VALUES (?, ?, ?, ?, ?, ?)',
        (
            transaction['user_id'],
            transaction['symbol'],
            transaction['quantity'],
            transaction['purchase_price'],
            transaction['sale_price'],
            transaction['sale_date'],
        ),
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid

# function to delete one transaction by id
def delete_transaction(transaction_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()

# function to get transactions from SQL
def get_all_transactions():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions')
    transactions = cursor.fetchall()
    conn.close()
    return transactions
