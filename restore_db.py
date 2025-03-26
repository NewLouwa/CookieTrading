import sqlite3
import os

# Delete existing database if it exists
if os.path.exists('trading.db'):
    os.remove('trading.db')

# Connect to database (this will create a new one)
conn = sqlite3.connect('trading.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS traders (
    count INTEGER DEFAULT 1,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    entry_price REAL NOT NULL,
    entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'open',
    comment TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS trading_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id INTEGER NOT NULL,
    exit_price REAL NOT NULL,
    profit_loss REAL NOT NULL,
    fee_percentage REAL NOT NULL,
    fee_amount REAL NOT NULL,
    comment TEXT,
    exit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (position_id) REFERENCES positions (id)
)
''')

# Insert the positions from the screenshot
cursor.execute('''
INSERT INTO positions (id, ingredient, quantity, entry_price, entry_date, comment, status)
VALUES 
    (1, 'BTR', 40, 1.00, '2025-03-26 21:18:35', 'LOOOOW AF', 'open'),
    (2, 'SEL', 29, 44.40, '2025-03-26 21:19:21', 'Pretty low', 'open')
''')

# Insert default trader count
cursor.execute('INSERT INTO traders (count) VALUES (1)')

# Commit changes and close connection
conn.commit()
conn.close()

print("Database restored successfully with the positions from the screenshot!") 