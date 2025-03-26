"""Tests for the TraderController."""

import pytest
from src.controllers.trader import TraderController
from src.utils.database import setup_database, get_db_connection
from src.models.position import Position

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
        cursor.execute("UPDATE traders SET count = 0")
        conn.commit()

@pytest.fixture
def trader():
    """Create a TraderController instance."""
    return TraderController()

def test_update_traders(trader, db):
    """Test updating trader count and fee calculation."""
    # Test with 0 traders (20% base fee)
    trader.update_traders(0)
    assert trader.current_fee == 20  # Base fee

    # Test with 5 traders (15% fee)
    trader.update_traders(5)
    assert trader.current_fee == 15  # 20 - (5 * 1)

    # Test with 25 traders (fee should not go below 0)
    trader.update_traders(25)
    assert trader.current_fee == 0

def test_fee_calculation(trader, db):
    """Test fee calculation."""
    # Test with 5 traders (15% fee)
    trader.update_traders(5)
    assert trader.current_fee == 15  # 20 - (5 * 1)

    # Test with 10 traders (10% fee)
    trader.update_traders(10)
    assert trader.current_fee == 10  # 20 - (10 * 1)

def test_simulate_close(trader, db):
    """Test position simulation with fees."""
    # Create a test position
    position = Position.create("BTR", 100, 575.21)
    
    # Set up 5 traders (15% fee)
    trader.update_traders(5)
    
    # Simulate profitable close
    profit_loss = position.simulate_close(600.00)
    fee_amount = round(abs(profit_loss) * (trader.current_fee / 100), 2)
    net_pl = profit_loss - fee_amount
    
    assert profit_loss == 2479.00  # (600 - 575.21) * 100
    assert fee_amount == 371.85    # 2479.00 * 0.15
    assert net_pl == 2107.15       # 2479.00 - 371.85

def test_non_interactive_operations(trader, db):
    """Test operations in non-interactive mode."""
    # Should not raise any errors
    trader.update_traders(5)

    with pytest.raises(RuntimeError, match="Cannot add position in non-interactive environment"):
        trader.add_position()
    
    with pytest.raises(RuntimeError, match="Cannot close position in non-interactive environment"):
        trader.close_position()
    
    with pytest.raises(RuntimeError, match="Cannot simulate close in non-interactive environment"):
        trader.simulate_close() 