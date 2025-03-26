"""Database utility functions."""

import sqlite3
from datetime import datetime
from .constants import DB_PATH

def setup_database():
    """Initialize the database with required tables."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Drop existing tables if they exist
        cursor.execute('DROP TABLE IF EXISTS trading_history')
        cursor.execute('DROP TABLE IF EXISTS positions')
        cursor.execute('DROP TABLE IF EXISTS traders')
        
        # Create traders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traders (
                count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingredient TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                entry_price REAL NOT NULL,
                entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'open',
                comment TEXT
            )
        ''')
        
        # Create trading history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id INTEGER,
                exit_price REAL,
                profit_loss REAL,
                fee_percentage REAL,
                fee_amount REAL,
                exit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                comment TEXT,
                FOREIGN KEY (position_id) REFERENCES positions (id)
            )
        ''')
        
        # Initialize traders table if empty
        cursor.execute('SELECT COUNT(*) FROM traders')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO traders (count) VALUES (0)')
        
        conn.commit()

def get_db_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH) 