"""Tests for the Trade model."""

import pytest
from datetime import datetime
from src.models.trade import Trade
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

def test_trade_creation(db):
    """Test trade creation through position closure."""
    position = Position.create("BTR", 100, 575.21, "Test position")
    profit_loss = position.close(600.00, "Closed for profit")
    
    trades = Trade.get_trading_history()
    assert len(trades) == 1
    assert trades[0].profit_loss == 2479.00
    assert trades[0].comment == "Closed for profit"

def test_trade_status_emoji(db):
    """Test trade status emoji based on profit/loss."""
    position = Position.create("BTR", 100, 575.21)
    position.close(600.00)  # Profit
    profit_trade = Trade.get_trading_history()[0]
    assert profit_trade.status_emoji == "📈"
    
    position = Position.create("CHC", 50, 1000.00)
    position.close(900.00)  # Loss
    loss_trade = Trade.get_trading_history()[1]
    assert loss_trade.status_emoji == "📉"

def test_trade_status_color(db):
    """Test trade status color based on profit/loss."""
    position = Position.create("BTR", 100, 575.21)
    position.close(600.00)  # Profit
    profit_trade = Trade.get_trading_history()[0]
    assert profit_trade.status_color == "green"
    
    position = Position.create("CHC", 50, 1000.00)
    position.close(900.00)  # Loss
    loss_trade = Trade.get_trading_history()[1]
    assert loss_trade.status_color == "red"

def test_get_total_profit_loss(db):
    """Test calculating total profit/loss."""
    # Create profitable trade
    position1 = Position.create("BTR", 100, 575.21)
    position1.close(600.00)  # +2479.00
    
    # Create losing trade
    position2 = Position.create("CHC", 50, 1000.00)
    position2.close(900.00)  # -5000.00
    
    total_pl = Trade.get_total_profit_loss()
    assert total_pl == -2521.00  # 2479.00 - 5000.00

def test_get_total_trades(db):
    """Test counting total number of trades."""
    assert Trade.get_total_trades() == 0
    
    position1 = Position.create("BTR", 100, 575.21)
    position1.close(600.00)
    assert Trade.get_total_trades() == 1
    
    position2 = Position.create("CHC", 50, 1000.00)
    position2.close(900.00)
    assert Trade.get_total_trades() == 2 