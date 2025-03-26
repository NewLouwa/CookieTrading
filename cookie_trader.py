#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box
from rich.prompt import Prompt, Confirm
import emoji

# Initialize Rich console
console = Console()

# Constants
INGREDIENTS = {
    'CRL': 'Cereal 🌾',
    'CHC': 'Chocolate 🍫',
    'BTR': 'Butter 🧈',
    'SCR': 'Sugar 🧂',
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

class CookieTrader:
    def __init__(self):
        self.db_path = 'cookie_trading.db'
        self.setup_database()
        
    def setup_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create traders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS traders (
                    count INTEGER DEFAULT 0
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
                    status TEXT DEFAULT 'open'
                )
            ''')
            
            # Create history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    position_id INTEGER,
                    exit_price REAL,
                    profit_loss REAL,
                    fee_percentage REAL,
                    fee_amount REAL,
                    exit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (position_id) REFERENCES positions (id)
                )
            ''')
            
            # Initialize traders count if not exists
            cursor.execute('SELECT count FROM traders')
            if not cursor.fetchone():
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

    def add_position(self, ingredient, quantity, price):
        """Add a new trading position."""
        if ingredient not in INGREDIENTS:
            console.print(f"[red]Invalid ingredient code: {ingredient}[/red]")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO positions (ingredient, quantity, entry_price)
                VALUES (?, ?, ?)
            ''', (ingredient, quantity, price))
            conn.commit()
            
        console.print(f"[green]Added position: {quantity} {INGREDIENTS[ingredient]} at {price}[/green]")

    def close_position(self, position_id, exit_price):
        """Close an existing position."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get position details
            cursor.execute('SELECT ingredient, quantity, entry_price FROM positions WHERE id = ? AND status = "open"', (position_id,))
            position = cursor.fetchone()
            
            if not position:
                console.print(f"[red]No open position found with ID {position_id}[/red]")
                return
            
            ingredient, quantity, entry_price = position
            fee_percentage = self.get_current_fee()
            
            # Calculate profit/loss
            gross_pl = (exit_price - entry_price) * quantity
            fee_amount = abs(gross_pl) * (fee_percentage / 100)
            net_pl = gross_pl - fee_amount
            
            # Record in history
            cursor.execute('''
                INSERT INTO trading_history (position_id, exit_price, profit_loss, fee_percentage, fee_amount)
                VALUES (?, ?, ?, ?, ?)
            ''', (position_id, exit_price, net_pl, fee_percentage, fee_amount))
            
            # Update position status
            cursor.execute('UPDATE positions SET status = "closed" WHERE id = ?', (position_id,))
            conn.commit()
            
        pl_color = "green" if net_pl > 0 else "red"
        console.print(f"[{pl_color}]Closed position {position_id}:")
        console.print(f"Profit/Loss: {net_pl:.2f} (Fee: {fee_amount:.2f} @ {fee_percentage}%)[/{pl_color}]")

    def simulate_close(self, position_id, exit_price):
        """Simulate closing a position to see potential profit/loss."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT ingredient, quantity, entry_price FROM positions WHERE id = ? AND status = "open"', (position_id,))
            position = cursor.fetchone()
            
            if not position:
                console.print(f"[red]No open position found with ID {position_id}[/red]")
                return
            
            ingredient, quantity, entry_price = position
            fee_percentage = self.get_current_fee()
            
            gross_pl = (exit_price - entry_price) * quantity
            fee_amount = abs(gross_pl) * (fee_percentage / 100)
            net_pl = gross_pl - fee_amount
            
            pl_color = "green" if net_pl > 0 else "red"
            console.print(f"\n[yellow]Simulation for position {position_id}:[/yellow]")
            console.print(f"[{pl_color}]Potential Profit/Loss: {net_pl:.2f}")
            console.print(f"Fee: {fee_amount:.2f} @ {fee_percentage}%[/{pl_color}]")

    def show_open_positions(self):
        """Display all open positions in a table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, ingredient, quantity, entry_price, entry_date FROM positions WHERE status = "open"')
            positions = cursor.fetchall()
            
        table = Table(title="Open Positions", box=box.ROUNDED)
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Ingredient", style="magenta")
        table.add_column("Quantity", justify="right", style="green")
        table.add_column("Entry Price", justify="right", style="yellow")
        table.add_column("Entry Date", style="blue")
        
        for pos in positions:
            table.add_row(
                str(pos[0]),
                f"{INGREDIENTS[pos[1]]}",
                str(pos[2]),
                f"{pos[3]:.2f}",
                pos[4]
            )
        
        console.print(table)

    def update_traders(self, count):
        """Update the number of traders."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE traders SET count = ?', (count,))
            conn.commit()
        
        new_fee = self.get_current_fee()
        console.print(f"[green]Updated traders count to {count}. New fee: {new_fee}%[/green]")

    def show_trading_history(self):
        """Display trading history in a colorful table with emojis."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    h.id,
                    p.ingredient,
                    p.quantity,
                    p.entry_price,
                    h.exit_price,
                    h.profit_loss,
                    h.fee_amount,
                    h.fee_percentage,
                    p.entry_date,
                    h.exit_date
                FROM trading_history h
                JOIN positions p ON h.position_id = p.id
                ORDER BY h.exit_date DESC
            ''')
            history = cursor.fetchall()
            
        if not history:
            console.print("[yellow]No trading history found.[/yellow]")
            return
            
        table = Table(title="Trading History 📜", box=box.ROUNDED)
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Ingredient", style="magenta")
        table.add_column("Qty", justify="right", style="green")
        table.add_column("Entry", justify="right", style="yellow")
        table.add_column("Exit", justify="right", style="yellow")
        table.add_column("P/L", justify="right", style="bold")
        table.add_column("Fee", justify="right", style="red")
        table.add_column("Entry Date", style="blue")
        table.add_column("Exit Date", style="blue")
        
        for trade in history:
            trade_id, ingredient, qty, entry, exit, pl, fee, fee_pct, entry_date, exit_date = trade
            
            # Determine trade status emoji
            if pl > 0:
                status_emoji = TRADE_EMOJIS['profit']
                pl_style = "green"
            elif pl < 0:
                status_emoji = TRADE_EMOJIS['loss']
                pl_style = "red"
            else:
                status_emoji = TRADE_EMOJIS['neutral']
                pl_style = "white"
            
            table.add_row(
                str(trade_id),
                f"{INGREDIENTS[ingredient]}",
                str(qty),
                f"${entry:.2f}",
                f"${exit:.2f}",
                f"[{pl_style}]{status_emoji} ${pl:.2f}[/{pl_style}]",
                f"${fee:.2f} ({fee_pct}%)",
                entry_date,
                exit_date
            )
        
        console.print(table)

    def show_menu(self):
        """Display the main menu and handle user input."""
        while True:
            console.print("\n[bold cyan]🍪 Cookie Trading Manager[/bold cyan]")
            console.print("\n1. 📈 Add Position")
            console.print("2. 📉 Close Position")
            console.print("3. 🔮 Simulate Close")
            console.print("4. 📊 Show Open Positions")
            console.print("5. 📜 Show Trading History")
            console.print("6. 👥 Update Traders Count")
            console.print("7. ❌ Exit")
            
            choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "7"])
            
            if choice == "1":
                # Create ingredient choices display string
                ingredient_choices = "/".join(INGREDIENTS.keys())
                ingredient_display = "\n".join([f"{code} {INGREDIENTS[code]}" for code in INGREDIENTS.keys()])
                console.print(f"\nAvailable ingredients:\n{ingredient_display}")
                ingredient = Prompt.ask(f"\nEnter ingredient code [{ingredient_choices}]")
                if ingredient.upper() not in INGREDIENTS:
                    console.print("[red]Invalid ingredient code![/red]")
                    continue
                quantity = int(Prompt.ask("Enter quantity"))
                price = float(Prompt.ask("Enter entry price"))
                self.add_position(ingredient.upper(), quantity, price)
                
            elif choice == "2":
                self.show_open_positions()
                position_id = int(Prompt.ask("Enter position ID to close"))
                exit_price = float(Prompt.ask("Enter exit price"))
                self.close_position(position_id, exit_price)
                
            elif choice == "3":
                self.show_open_positions()
                position_id = int(Prompt.ask("Enter position ID to simulate"))
                exit_price = float(Prompt.ask("Enter hypothetical exit price"))
                self.simulate_close(position_id, exit_price)
                
            elif choice == "4":
                self.show_open_positions()
                
            elif choice == "5":
                self.show_trading_history()
                
            elif choice == "6":
                count = int(Prompt.ask("Enter new trader count"))
                self.update_traders(count)
                
            elif choice == "7":
                console.print("[yellow]Goodbye! 👋[/yellow]")
                break

if __name__ == "__main__":
    trader = CookieTrader()
    trader.show_menu() 