"""Tests for database utilities."""

import pytest
import sqlite3
from src.utils.database import setup_database, get_db_connection

def test_setup_database():
    """Test database initialization."""
    setup_database()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('traders', 'positions', 'trading_history')
        """)
        tables = cursor.fetchall()
        assert len(tables) == 3
        
        # Check traders table structure
        cursor.execute("PRAGMA table_info(traders)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        assert "count" in column_names
        assert "last_updated" in column_names
        
        # Check positions table structure
        cursor.execute("PRAGMA table_info(positions)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        assert "id" in column_names
        assert "ingredient" in column_names
        assert "quantity" in column_names
        assert "entry_price" in column_names
        assert "entry_date" in column_names
        assert "last_updated" in column_names
        assert "status" in column_names
        assert "comment" in column_names
        
        # Check trading_history table structure
        cursor.execute("PRAGMA table_info(trading_history)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        assert "id" in column_names
        assert "position_id" in column_names
        assert "exit_price" in column_names
        assert "profit_loss" in column_names
        assert "fee_percentage" in column_names
        assert "fee_amount" in column_names
        assert "exit_date" in column_names
        assert "comment" in column_names
        
        # Check if traders table is initialized with count = 0
        cursor.execute("SELECT count FROM traders")
        count = cursor.fetchone()[0]
        assert count == 0

def test_database_connection():
    """Test database connection handling."""
    conn = get_db_connection()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()

def test_database_transactions():
    """Test database transaction handling."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Test insert
        cursor.execute("INSERT INTO positions (ingredient, quantity, entry_price) VALUES (?, ?, ?)",
                      ("BTR", 100, 575.21))
        conn.commit()
        
        # Verify insert
        cursor.execute("SELECT * FROM positions WHERE ingredient = ?", ("BTR",))
        result = cursor.fetchone()
        assert result is not None
        assert result[1] == "BTR"
        assert result[2] == 100
        assert result[3] == 575.21 