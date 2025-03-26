"""Trade model for trading history."""

from datetime import datetime
from ..utils.database import get_db_connection
from ..utils.constants import INGREDIENTS, TRADE_EMOJIS

class Trade:
    def __init__(self, id=None, ingredient=None, quantity=None, entry_price=None,
                 exit_price=None, profit_loss=None, fee_percentage=None, fee_amount=None,
                 exit_date=None, comment=None):
        self.id = id
        self.ingredient = ingredient
        self.quantity = quantity
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.profit_loss = profit_loss
        self.fee_percentage = fee_percentage
        self.fee_amount = fee_amount
        self.exit_date = exit_date or datetime.now()
        self.comment = comment

    @property
    def status_emoji(self):
        """Get trade status emoji."""
        if self.profit_loss > 0:
            return TRADE_EMOJIS['profit']
        elif self.profit_loss < 0:
            return TRADE_EMOJIS['loss']
        return TRADE_EMOJIS['neutral']

    @property
    def status_color(self):
        """Get trade status color."""
        return "green" if self.profit_loss >= 0 else "red"

    @classmethod
    def get_trading_history(cls):
        """Get all trading history."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    th.id,
                    p.ingredient,
                    p.quantity,
                    p.entry_price,
                    th.exit_price,
                    th.profit_loss,
                    th.fee_percentage,
                    th.fee_amount,
                    th.exit_date,
                    th.comment
                FROM trading_history th
                JOIN positions p ON th.position_id = p.id
                ORDER BY th.exit_date DESC
            ''')
            return [cls(*row) for row in cursor.fetchall()]

    @classmethod
    def get_total_profit_loss(cls):
        """Get total profit/loss from all trades."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(profit_loss) FROM trading_history')
            return cursor.fetchone()[0] or 0

    @classmethod
    def get_total_trades(cls):
        """Get total number of trades."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM trading_history')
            return cursor.fetchone()[0] 