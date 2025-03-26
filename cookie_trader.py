#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box
from rich.prompt import Prompt, Confirm
import emoji
import re
from rich.panel import Panel

# Initialize Rich console
console = Console()

# Constants
INGREDIENTS = {
    'CRL': 'Cereal 🌾',
    'CHC': 'Chocolate 🍫',
    'BTR': 'Butter 🧈',
    'SUC': 'Sugar 🧂',
    'NOI': 'Walnut 🥜',
    'SEL': 'Salt 🧂',
    'VNL': 'Vanilla 🍶',
    'OEUF': 'Eggs 🥚'
}

# Trade status emojis
TRADE_EMOJIS = {
    'profit': '📈',
    'loss': '📉',
    'neutral': '➡️'
}

BASE_FEE = 20  # Base fee percentage
FEE_REDUCTION_PER_TRADER = 1  # Fee reduction percentage per trader

def show_available_units():
    """Display available units in a formatted table."""
    table = Table(title="Available Units 📏", box=box.ROUNDED)
    table.add_column("Code", style="cyan", justify="right")
    table.add_column("Name", style="green")
    table.add_column("Power", style="yellow")
    
    for code, (_, name, power) in UNIT_MULTIPLIERS.items():
        table.add_row(code, name, power)
    
    console.print(table)

def parse_price(price_str):
    """Convert a price string to a float value."""
    price_str = price_str.strip().replace('$', '').strip()
    if not price_str:
        return 0.0
    
    try:
        return float(price_str)
    except ValueError:
        raise ValueError("Invalid price format. Enter a number (e.g., 123.45 or $123.45)")

def format_price(price):
    """Format a number into game currency format."""
    if price == 0:
        return "$0.00"
    
    return f"${abs(price):.2f}"

class CookieTrader:
    def __init__(self):
        """Initialize the CookieTrader with database."""
        self.db_path = 'trading.db'
        self.setup_database()
        
    def setup_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create traders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS traders (
                    count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create positions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingredient TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    entry_price REAL NOT NULL,
                    entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'open',
                    comment TEXT
                )
            ''')
            
            # Create trading history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    position_id INTEGER,
                    exit_price REAL,
                    profit_loss REAL,
                    fee_percentage REAL,
                    fee_amount REAL,
                    exit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    comment TEXT,
                    FOREIGN KEY (position_id) REFERENCES positions (id)
                )
            ''')
            
            # Initialize traders table if empty
            cursor.execute('SELECT COUNT(*) FROM traders')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO traders (count) VALUES (0)')
            
            conn.commit()

    def get_current_fee(self):
        """Calculate current fee percentage based on number of traders."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT count FROM traders')
            trader_count = cursor.fetchone()[0]
            
        fee = max(0, BASE_FEE - (trader_count * FEE_REDUCTION_PER_TRADER))
        return fee

    def get_comment(self, prompt_text):
        """Get optional comment from user."""
        comment = Prompt.ask(prompt_text, default="")
        if comment:
            return comment[:500]  # Limit to 500 chars
        return ""

    def add_position(self, ingredient, quantity, price, comment=""):
        """Add a new trading position."""
        if ingredient not in INGREDIENTS:
            console.print(f"[red]Invalid ingredient code: {ingredient}[/red]")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO positions (ingredient, quantity, entry_price, comment)
                VALUES (?, ?, ?, ?)
            ''', (ingredient, quantity, price, comment))
            conn.commit()
            
        output = f"\n[green]📈 Position Opened:[/green]"
        output += f"\nIngredient: {quantity} {INGREDIENTS[ingredient]}"
        output += f"\nEntry Price: {format_price(price)}"
        if comment:
            output += f"\nComment: {comment}"
        console.print(output)

    def close_position(self, position_id, exit_price, comment=""):
        """Close an existing position."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get position details
            cursor.execute('SELECT ingredient, quantity, entry_price, status FROM positions WHERE id = ?', (position_id,))
            position = cursor.fetchone()
            
            if not position:
                console.print(f"[red]No open position found with ID {position_id}[/red]")
                return
            
            ingredient, total_quantity, entry_price, status = position
            
            if status == 'closed':
                console.print(f"[red]Position {position_id} is already closed![/red]")
                return
            
            # Ask for number of shares to sell
            while True:
                try:
                    sell_quantity = int(Prompt.ask(f"Enter number of shares to sell (max {total_quantity})"))
                    if sell_quantity <= 0:
                        console.print("[red]Quantity must be greater than 0![/red]")
                        continue
                    if sell_quantity > total_quantity:
                        console.print(f"[red]Cannot sell more shares than you have! Maximum available: {total_quantity}[/red]")
                        continue
                    break
                except ValueError:
                    console.print("[red]Please enter a valid number![/red]")
            
            # Calculate profit/loss
            gross_pl = (exit_price - entry_price) * sell_quantity
            fee_percentage = self.get_current_fee()
            fee_amount = abs(gross_pl) * (fee_percentage / 100)
            net_pl = gross_pl - fee_amount
            
            # Update position status
            if sell_quantity == total_quantity:
                # Close the entire position
                cursor.execute('''
                    UPDATE positions 
                    SET status = 'closed',
                        last_updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (position_id,))
            else:
                # Update the remaining quantity
                cursor.execute('''
                    UPDATE positions 
                    SET quantity = quantity - ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (sell_quantity, position_id))
            
            # Record in history
            cursor.execute('''
                INSERT INTO trading_history 
                (position_id, exit_price, profit_loss, fee_percentage, fee_amount, comment)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (position_id, exit_price, net_pl, fee_percentage, fee_amount, comment))
            
            conn.commit()
            
        pl_color = "green" if net_pl > 0 else "red"
        pl_emoji = "📈" if net_pl > 0 else "📉"
        output = f"\n[{pl_color}]{pl_emoji} Position Closed:[/{pl_color}]"
        output += f"\nPosition ID: {position_id}"
        output += f"\nShares Sold: {sell_quantity} of {total_quantity}"
        output += f"\nExit Price: {format_price(exit_price)}"
        output += f"\nGross P/L: {format_price(gross_pl)}"
        output += f"\nFee: {format_price(fee_amount)} @ {fee_percentage}%"
        output += f"\nNet P/L: {format_price(net_pl)}"
        if comment:
            output += f"\nComment: {comment}"
        console.print(output)

    def get_position(self, position_id):
        """Get a position by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, ingredient, quantity, entry_price FROM positions WHERE id = ? AND status = "open"', (position_id,))
            return cursor.fetchone()

    def simulate_close(self, position_id, exit_price):
        """Simulate closing a position to see potential profit/loss."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT ingredient, quantity, entry_price FROM positions WHERE id = ? AND status = "open"', (position_id,))
            position = cursor.fetchone()
            
            if not position:
                console.print(f"[red]No open position found with ID {position_id}[/red]")
            else:
                ingredient, total_quantity, entry_price = position
                
                # Ask for number of shares to simulate
                while True:
                    try:
                        sell_quantity = int(Prompt.ask(f"Enter number of shares to simulate (max {total_quantity})"))
                        if sell_quantity <= 0:
                            console.print("[red]Quantity must be greater than 0![/red]")
                            continue
                        if sell_quantity > total_quantity:
                            console.print(f"[red]Cannot simulate more shares than you have! Maximum available: {total_quantity}[/red]")
                            continue
                        break
                    except ValueError:
                        console.print("[red]Please enter a valid number![/red]")
                
                gross_pl = (exit_price - entry_price) * sell_quantity
                fee_percentage = self.get_current_fee()
                fee_amount = abs(gross_pl) * (fee_percentage / 100)
                net_pl = gross_pl - fee_amount
                
                pl_color = "green" if net_pl > 0 else "red"
                pl_emoji = "📈" if net_pl > 0 else "📉"
                output = f"\n[{pl_color}]{pl_emoji} Simulation Results:[/{pl_color}]"
                output += f"\nPosition ID: {position_id}"
                output += f"\nShares to Sell: {sell_quantity} of {total_quantity}"
                output += f"\nHypothetical Exit Price: {format_price(exit_price)}"
                output += f"\nPotential Gross P/L: {format_price(gross_pl)}"
                output += f"\nFee: {format_price(fee_amount)} @ {fee_percentage}%"
                output += f"\nPotential Net P/L: {format_price(net_pl)}"
                console.print(output)
        
        self.wait_for_user()

    def show_open_positions(self):
        """Display all open positions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, ingredient, quantity, entry_price, entry_date, comment
                FROM positions 
                WHERE status = 'open'
                ORDER BY entry_date DESC
            ''')
            positions = cursor.fetchall()
            
            if not positions:
                console.print("[yellow]No open positions[/yellow]")
            else:
                table = Table(title="Open Positions", box=box.ROUNDED)
                table.add_column("ID", justify="right", style="cyan")
                table.add_column("Ingredient", style="magenta")
                table.add_column("Quantity", justify="right")
                table.add_column("Entry Price", justify="right")
                table.add_column("Entry Date", style="blue")
                table.add_column("Comment", style="italic")
                
                for pos in positions:
                    table.add_row(
                        str(pos[0]),
                        f"{pos[1]} {INGREDIENTS[pos[1]]}",
                        str(pos[2]),
                        format_price(pos[3]),
                        pos[4],
                        pos[5] or ""
                    )
                
                console.print(table)
        
        self.wait_for_user()

    def update_traders(self, count):
        """Update the number of traders."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE traders SET count = ?', (count,))
            conn.commit()
        
        new_fee = self.get_current_fee()
        console.print(f"[green]Updated traders count to {count}. New fee: {new_fee}%[/green]")

    def show_trading_history(self):
        """Display trading history."""
        with sqlite3.connect(self.db_path) as conn:
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
            trades = cursor.fetchall()
            
            if not trades:
                console.print("[yellow]No trading history[/yellow]")
            else:
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
                    pl_color = "green" if trade[5] >= 0 else "red"
                    pl_emoji = TRADE_EMOJIS['profit'] if trade[5] >= 0 else TRADE_EMOJIS['loss']
                    
                    table.add_row(
                        str(trade[0]),
                        f"{trade[1]} {INGREDIENTS[trade[1]]}",
                        str(trade[2]),
                        format_price(trade[3]),
                        format_price(trade[4]),
                        f"{pl_emoji} [{pl_color}]{format_price(trade[5])}[/{pl_color}]",
                        f"{trade[6]}%",
                        format_price(trade[7]),
                        trade[8],
                        trade[9] or ""
                    )
                
                console.print(table)
        
        self.wait_for_user()

    def get_dashboard_info(self):
        """Get current trading dashboard information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get trader count and current fee
            cursor.execute('SELECT count FROM traders LIMIT 1')
            trader_count = cursor.fetchone()[0]
            current_fee = self.get_current_fee()
            
            # Get open positions count
            cursor.execute('SELECT COUNT(*) FROM positions WHERE status = "open"')
            open_positions = cursor.fetchone()[0]
            
            # Get total profit/loss
            cursor.execute('SELECT SUM(profit_loss) FROM trading_history')
            total_pl = cursor.fetchone()[0] or 0
            
            # Get total trades
            cursor.execute('SELECT COUNT(*) FROM trading_history')
            total_trades = cursor.fetchone()[0]
            
            return {
                'traders': trader_count,
                'fee': current_fee,
                'open_positions': open_positions,
                'total_pl': total_pl,
                'total_trades': total_trades
            }

    def show_dashboard(self):
        """Display the trading dashboard."""
        info = self.get_dashboard_info()
        
        # Create a table for the dashboard
        table = Table(box=box.ROUNDED, show_header=False, width=60)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="yellow")
        
        # Add rows with emojis and formatting
        table.add_row(
            "👥 Traders",
            f"[bold]{info['traders']}[/bold] (Fee: [green]{info['fee']}%[/green])"
        )
        table.add_row(
            "📊 Open Positions",
            f"[bold]{info['open_positions']}[/bold] active trades"
        )
        
        # Format total P/L with color
        pl_color = "green" if info['total_pl'] >= 0 else "red"
        pl_emoji = "📈" if info['total_pl'] >= 0 else "📉"
        table.add_row(
            f"{pl_emoji} Total P/L",
            f"[{pl_color}]{format_price(info['total_pl'])}[/{pl_color}]"
        )
        
        table.add_row(
            "🔄 Total Trades",
            f"[bold]{info['total_trades']}[/bold] completed"
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

    def simulate_trade(self, ingredient, quantity, entry_price, exit_price):
        """Simulate a complete trade with entry and exit to see potential profit/loss."""
        if ingredient not in INGREDIENTS:
            console.print(f"[red]Invalid ingredient code: {ingredient}[/red]")
        else:
            gross_pl = (exit_price - entry_price) * quantity
            fee_percentage = self.get_current_fee()
            fee_amount = abs(gross_pl) * (fee_percentage / 100)
            net_pl = gross_pl - fee_amount
            
            pl_color = "green" if net_pl > 0 else "red"
            pl_emoji = "📈" if net_pl > 0 else "📉"
            output = f"\n[{pl_color}]{pl_emoji} Trade Simulation:[/{pl_color}]"
            output += f"\nIngredient: {quantity} {INGREDIENTS[ingredient]}"
            output += f"\nEntry Price: {format_price(entry_price)}"
            output += f"\nExit Price: {format_price(exit_price)}"
            output += f"\nPotential Gross P/L: {format_price(gross_pl)}"
            output += f"\nFee: {format_price(fee_amount)} @ {fee_percentage}%"
            output += f"\nPotential Net P/L: {format_price(net_pl)}"
            console.print(output)
        
        self.wait_for_user()

    def wait_for_user(self):
        """Wait for user to press Enter before continuing."""
        Prompt.ask("\nPress Enter to continue", default="")

    def show_menu(self):
        """Display the main menu and handle user input."""
        while True:
            console.clear()
            console.print("[bold cyan]🍪 Cookie Trading Manager[/bold cyan]")
            
            # Show dashboard at the top
            self.show_dashboard()
            
            # Position Actions (Green)
            console.print("\n[bold green]Position Actions[/bold green]")
            console.print("1. 📈 Open Position")
            console.print("2. 📉 Close Position")
            console.print("3. 🔮 Simulate Close")
            console.print("4. 🎯 Simulate Trade")
            
            # View Actions (Blue)
            console.print("\n[bold blue]View Actions[/bold blue]")
            console.print("5. 📊 Show Open Positions")
            console.print("6. 📜 Show Trading History")
            
            # Settings & Exit (Yellow/Red)
            console.print("\n[bold yellow]Settings & Exit[/bold yellow]")
            console.print("7. 👥 Update Traders Count")
            console.print("[bold red]8. ❌ Exit[/bold red]")
            
            choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                # Create ingredient choices display string
                ingredient_choices = "/".join(INGREDIENTS.keys())
                ingredient_display = "\n".join([f"{code} {INGREDIENTS[code]}" for code in INGREDIENTS.keys()])
                console.print(f"\nAvailable ingredients:\n{ingredient_display}")
                ingredient = Prompt.ask(f"\nEnter ingredient code [{ingredient_choices}]")
                if ingredient.upper() not in INGREDIENTS:
                    console.print("[red]Invalid ingredient code![/red]")
                    continue
                quantity = int(Prompt.ask("Enter number of shares"))
                
                # Handle price input
                while True:
                    try:
                        price_str = Prompt.ask("Enter entry price (e.g., 123.45 or $123.45)")
                        price = parse_price(price_str)
                        break
                    except ValueError as e:
                        console.print(f"[red]{str(e)}[/red]")
                
                # Get optional comment
                comment = self.get_comment("Add a comment (optional)")
                
                self.add_position(ingredient.upper(), quantity, price, comment)
                
            elif choice == "2":
                self.show_open_positions()
                position_id = int(Prompt.ask("Enter position ID to close"))
                
                # Handle exit price input
                while True:
                    try:
                        price_str = Prompt.ask("Enter exit price (e.g., 123.45 or $123.45)")
                        exit_price = parse_price(price_str)
                        break
                    except ValueError as e:
                        console.print(f"[red]{str(e)}[/red]")
                
                # Get optional comment
                comment = self.get_comment("Add a comment (optional)")
                
                self.close_position(position_id, exit_price, comment)
                
            elif choice == "3":
                self.show_open_positions()
                position_id = int(Prompt.ask("Enter position ID to simulate"))
                
                # Handle hypothetical price input
                while True:
                    try:
                        price_str = Prompt.ask("Enter hypothetical exit price (e.g., 123.45 or $123.45)")
                        exit_price = parse_price(price_str)
                        break
                    except ValueError as e:
                        console.print(f"[red]{str(e)}[/red]")
                
                self.simulate_close(position_id, exit_price)
                
            elif choice == "4":
                # Create ingredient choices display string
                ingredient_choices = "/".join(INGREDIENTS.keys())
                ingredient_display = "\n".join([f"{code} {INGREDIENTS[code]}" for code in INGREDIENTS.keys()])
                console.print(f"\nAvailable ingredients:\n{ingredient_display}")
                ingredient = Prompt.ask(f"\nEnter ingredient code [{ingredient_choices}]")
                if ingredient.upper() not in INGREDIENTS:
                    console.print("[red]Invalid ingredient code![/red]")
                    continue
                
                quantity = int(Prompt.ask("Enter number of shares"))
                
                # Handle entry price input
                while True:
                    try:
                        price_str = Prompt.ask("Enter entry price (e.g., 123.45 or $123.45)")
                        entry_price = parse_price(price_str)
                        break
                    except ValueError as e:
                        console.print(f"[red]{str(e)}[/red]")
                
                # Handle exit price input
                while True:
                    try:
                        price_str = Prompt.ask("Enter hypothetical exit price (e.g., 123.45 or $123.45)")
                        exit_price = parse_price(price_str)
                        break
                    except ValueError as e:
                        console.print(f"[red]{str(e)}[/red]")
                
                self.simulate_trade(ingredient.upper(), quantity, entry_price, exit_price)
                
            elif choice == "5":
                self.show_open_positions()
                
            elif choice == "6":
                self.show_trading_history()
                
            elif choice == "7":
                count = int(Prompt.ask("Enter new trader count"))
                self.update_traders(count)
                
            elif choice == "8":
                console.print("[red]Goodbye! 👋[/red]")
                break

if __name__ == "__main__":
    trader = CookieTrader()
    trader.show_menu() 