"""Tests for the Position model."""

import pytest
from datetime import datetime
from src.models.position import Position
from src.utils.database import setup_database, get_db_connection

@pytest.fixture
def db():
    """Setup test database."""
    setup_database()
    yield
    # Cleanup after tests
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM positions")
        cursor.execute("DELETE FROM trading_history")
        conn.commit()

def test_create_position(db):
    """Test creating a new position."""
    position = Position.create("BTR", 100, 575.21, "Test position")
    
    assert position.ingredient == "BTR"
    assert position.quantity == 100
    assert position.entry_price == 575.21
    assert position.comment == "Test position"
    assert position.status == "open"
    assert isinstance(position.entry_date, datetime)

def test_get_open_positions(db):
    """Test retrieving open positions."""
    # Create multiple positions
    Position.create("BTR", 100, 575.21, "First position")
    Position.create("CHC", 50, 1234.56, "Second position")
    
    positions = Position.get_open_positions()
    
    assert len(positions) == 2
    assert positions[0].ingredient == "BTR"
    assert positions[1].ingredient == "CHC"

def test_close_position(db):
    """Test closing a position."""
    position = Position.create("BTR", 100, 575.21, "Test position")
    profit_loss = position.close(600.00, "Closed for profit")
    
    assert profit_loss == 2479.00  # (600 - 575.21) * 100
    assert position.status == "closed"
    
    # Verify position is no longer in open positions
    open_positions = Position.get_open_positions()
    assert len(open_positions) == 0

def test_simulate_close(db):
    """Test simulating position closure."""
    position = Position.create("BTR", 100, 575.21, "Test position")
    profit_loss = position.simulate_close(600.00)
    
    assert profit_loss == 2479.00  # (600 - 575.21) * 100

def test_ingredient_display(db):
    """Test ingredient display formatting."""
    position = Position.create("BTR", 100, 575.21)
    assert position.ingredient_display == "BTR Butter 🧈" 