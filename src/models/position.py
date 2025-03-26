"""Position model for trading positions."""

from datetime import datetime
from ..utils.database import get_db_connection
from ..utils.constants import INGREDIENTS

class Position:
    def __init__(self, id=None, ingredient=None, quantity=None, entry_price=None, 
                 entry_date=None, status='open', comment=None):
        self.id = id
        self.ingredient = ingredient
        self.quantity = quantity
        self.entry_price = entry_price
        self.entry_date = entry_date or datetime.now()
        self.status = status
        self.comment = comment

    @property
    def ingredient_display(self):
        """Get formatted ingredient name with emoji."""
        return f"{self.ingredient} {INGREDIENTS[self.ingredient]}"

    @classmethod
    def create(cls, ingredient, quantity, entry_price, comment=""):
        """Create a new position."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO positions (ingredient, quantity, entry_price, comment)
                VALUES (?, ?, ?, ?)
            ''', (ingredient, quantity, entry_price, comment))
            conn.commit()
            return cls(
                id=cursor.lastrowid,
                ingredient=ingredient,
                quantity=quantity,
                entry_price=entry_price,
                comment=comment
            )

    @classmethod
    def get_open_positions(cls):
        """Get all open positions."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, ingredient, quantity, entry_price, entry_date, comment
                FROM positions 
                WHERE status = 'open'
                ORDER BY entry_date DESC
            ''')
            return [cls(*row) for row in cursor.fetchall()]

    def close(self, exit_price, comment=""):
        """Close the position."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Calculate profit/loss with proper rounding
            profit_loss = round((exit_price - self.entry_price) * self.quantity, 2)
            
            # Update position status
            cursor.execute('''
                UPDATE positions 
                SET status = 'closed',
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (self.id,))
            
            # Record in history
            cursor.execute('''
                INSERT INTO trading_history 
                (position_id, exit_price, profit_loss, fee_percentage, fee_amount, comment)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.id, exit_price, profit_loss, 0, 0, comment))
            
            conn.commit()
            
            # Update status in memory
            self.status = 'closed'
            
            return profit_loss

    def simulate_close(self, exit_price):
        """Simulate closing the position."""
        profit_loss = round((exit_price - self.entry_price) * self.quantity, 2)
        return profit_loss 