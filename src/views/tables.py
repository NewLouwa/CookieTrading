"""Table view components for displaying positions and history."""

from rich.console import Console
from rich.table import Table
from ..models.position import Position
from ..models.trade import Trade
from ..utils.formatting import format_price

console = Console()

def show_open_positions():
    """Display all open positions."""
    positions = Position.get_open_positions()
    
    if not positions:
        console.print("[yellow]No open positions[/yellow]")
        return
    
    table = Table(title="Open Positions", box=box.ROUNDED)
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Ingredient", style="magenta")
    table.add_column("Quantity", justify="right")
    table.add_column("Entry Price", justify="right")
    table.add_column("Entry Date", style="blue")
    table.add_column("Comment", style="italic")
    
    for pos in positions:
        table.add_row(
            str(pos.id),
            pos.ingredient_display,
            str(pos.quantity),
            format_price(pos.entry_price),
            pos.entry_date.strftime("%Y-%m-%d %H:%M:%S"),
            pos.comment or ""
        )
    
    console.print(table)

def show_trading_history():
    """Display trading history."""
    trades = Trade.get_trading_history()
    
    if not trades:
        console.print("[yellow]No trading history[/yellow]")
        return
    
    table = Table(title="Trading History", box=box.ROUNDED)
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Ingredient", style="magenta")
    table.add_column("Quantity", justify="right")
    table.add_column("Entry", justify="right")
    table.add_column("Exit", justify="right")
    table.add_column("P/L", justify="right")
    table.add_column("Fee", justify="right")
    table.add_column("Exit Date", style="blue")
    table.add_column("Comment", style="italic")
    
    for trade in trades:
        table.add_row(
            str(trade.id),
            f"{trade.ingredient} {INGREDIENTS[trade.ingredient]}",
            str(trade.quantity),
            format_price(trade.entry_price),
            format_price(trade.exit_price),
            f"{trade.status_emoji} [{trade.status_color}]{format_price(trade.profit_loss)}[/{trade.status_color}]",
            f"{trade.fee_percentage}%",
            format_price(trade.fee_amount),
            trade.exit_date.strftime("%Y-%m-%d %H:%M:%S"),
            trade.comment or ""
        )
    
    console.print(table) 