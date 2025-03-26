"""Dashboard view component."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
from ..models.trade import Trade
from ..models.position import Position
from ..utils.constants import INGREDIENTS

console = Console()

def show_dashboard():
    """Display the trading dashboard."""
    # Get dashboard information
    open_positions = Position.get_open_positions()
    total_pl = Trade.get_total_profit_loss()
    total_trades = Trade.get_total_trades()
    
    # Create a table for the dashboard
    table = Table(box=None, show_header=False, width=60)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="yellow")
    
    # Add rows with emojis and formatting
    table.add_row(
        "👥 Traders",
        f"[bold]0[/bold] (Fee: [green]20%[/green])"
    )
    table.add_row(
        "📊 Open Positions",
        f"[bold]{len(open_positions)}[/bold] active trades"
    )
    
    # Format total P/L with color
    pl_color = "green" if total_pl >= 0 else "red"
    pl_emoji = "📈" if total_pl >= 0 else "📉"
    table.add_row(
        f"{pl_emoji} Total P/L",
        f"[{pl_color}]{total_pl:.2f}[/{pl_color}]"
    )
    
    table.add_row(
        "🔄 Total Trades",
        f"[bold]{total_trades}[/bold] completed"
    )
    
    # Add a title panel
    panel = Panel(
        table,
        title="[bold cyan]Trading Dashboard[/bold cyan]",
        subtitle=f"[dim]Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]"
    )
    
    console.print("\n")
    console.print(panel)
    console.print("\n") 