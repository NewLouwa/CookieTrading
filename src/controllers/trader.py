"""Trader controller with business logic."""

from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.output import create_output
from ..models.position import Position
from ..models.trade import Trade
from ..utils.constants import INGREDIENTS, BASE_FEE, FEE_REDUCTION_PER_TRADER
from ..utils.formatting import parse_price, format_price, get_comment
from ..utils.database import get_db_connection

console = Console()

# Only create PromptSession if we're in an interactive environment
try:
    session = PromptSession()
except Exception:
    # For testing or non-interactive environments
    session = None

class TraderController:
    def __init__(self):
        self.trader_count = 0
        self.current_fee = BASE_FEE

    def get_current_fee(self):
        """Calculate current fee percentage based on number of traders."""
        return max(0, BASE_FEE - (self.trader_count * FEE_REDUCTION_PER_TRADER))

    def update_traders(self, count):
        """Update the number of traders."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE traders 
                SET count = ?,
                    last_updated = CURRENT_TIMESTAMP
            ''', (count,))
            conn.commit()
        
        self.trader_count = count
        self.current_fee = self.get_current_fee()
        console.print(f"[green]Updated trader count to {count} (Fee: {self.current_fee}%)[/green]")

    def add_position(self):
        """Add a new trading position."""
        if not session:
            raise RuntimeError("Cannot add position in non-interactive environment")
            
        # Show available ingredients
        ingredient_choices = "/".join(INGREDIENTS.keys())
        ingredient_display = "\n".join([f"{code} {INGREDIENTS[code]}" for code in INGREDIENTS.keys()])
        console.print(f"\nAvailable ingredients:\n{ingredient_display}")
        
        # Get position details
        ingredient = session.prompt(f"\nEnter ingredient code [{ingredient_choices}]")
        if ingredient.upper() not in INGREDIENTS:
            console.print("[red]Invalid ingredient code![/red]")
            return
        
        try:
            quantity = int(session.prompt("Enter quantity"))
            price_str = session.prompt("Enter entry price (e.g., 123.45 or $123.45)")
            price = parse_price(price_str)
            comment = get_comment("Add a comment (optional)")
            
            position = Position.create(ingredient.upper(), quantity, price, comment)
            console.print(f"[green]Added position: {quantity} {INGREDIENTS[ingredient.upper()]} at {format_price(price)}[/green]")
            
        except ValueError as e:
            console.print(f"[red]{str(e)}[/red]")

    def close_position(self):
        """Close an existing position."""
        if not session:
            raise RuntimeError("Cannot close position in non-interactive environment")
            
        from ..views.tables import show_open_positions
        
        show_open_positions()
        try:
            position_id = int(session.prompt("Enter position ID to close"))
            price_str = session.prompt("Enter exit price (e.g., 123.45 or $123.45)")
            exit_price = parse_price(price_str)
            comment = get_comment("Add a comment (optional)")
            
            position = Position.get_open_positions()[position_id - 1]
            profit_loss = position.close(exit_price, comment)
            
            pl_color = "green" if profit_loss >= 0 else "red"
            console.print(f"[{pl_color}]Closed position: {format_price(profit_loss)}[/{pl_color}]")
            
        except (ValueError, IndexError) as e:
            console.print(f"[red]Error: {str(e)}[/red]")

    def simulate_close(self):
        """Simulate closing a position."""
        if not session:
            raise RuntimeError("Cannot simulate close in non-interactive environment")
            
        from ..views.tables import show_open_positions
        
        show_open_positions()
        try:
            position_id = int(session.prompt("Enter position ID to simulate"))
            price_str = session.prompt("Enter hypothetical exit price (e.g., 123.45 or $123.45)")
            exit_price = parse_price(price_str)
            
            position = Position.get_open_positions()[position_id - 1]
            profit_loss = position.simulate_close(exit_price)
            fee_amount = abs(profit_loss) * (self.current_fee / 100)
            net_pl = profit_loss - fee_amount
            
            pl_color = "green" if net_pl >= 0 else "red"
            console.print(f"\nSimulation Results:")
            console.print(f"Gross P/L: [{pl_color}]{format_price(profit_loss)}[/{pl_color}]")
            console.print(f"Fee ({self.current_fee}%): {format_price(fee_amount)}")
            console.print(f"Net P/L: [{pl_color}]{format_price(net_pl)}[/{pl_color}]")
            
        except (ValueError, IndexError) as e:
            console.print(f"[red]Error: {str(e)}[/red]") 