"""Pytest configuration file with common fixtures."""

import pytest
import os
import sqlite3
from src.utils.database import setup_database, get_db_connection
from src.utils.constants import DB_PATH
from src.models import position, trade
from src.controllers import trader

@pytest.fixture(autouse=True)
def test_db():
    """Setup test database for all tests."""
    # Use a test-specific database file
    test_db_path = "test_trading.db"
    
    # Store original DB_PATH
    original_db_path = DB_PATH
    
    # Update DB_PATH in all relevant modules
    import src.utils.constants
    src.utils.constants.DB_PATH = test_db_path
    position.DB_PATH = test_db_path
    trade.DB_PATH = test_db_path
    trader.DB_PATH = test_db_path
    
    # Remove existing test database if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize test database
    setup_database()
    
    yield
    
    # Cleanup after tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Restore original DB_PATH in all modules
    src.utils.constants.DB_PATH = original_db_path
    position.DB_PATH = original_db_path
    trade.DB_PATH = original_db_path
    trader.DB_PATH = original_db_path 