#!/usr/bin/env python3
"""
Cookie Trading Manager - A terminal-based trading simulation application.

This application provides a user-friendly interface for managing trading positions
of various cookie ingredients. It features real-time profit/loss calculation,
position tracking, and a dynamic fee system based on the number of traders.

Key features:
- Position management (open, close, simulate)
- Real-time trading dashboard
- Dynamic fee calculation
- Trading history tracking
- Beautiful terminal UI using Rich library
"""

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
from src.utils.formatting import parse_price, format_price, get_comment, get_quantity, custom_prompt

# Initialize Rich console for beautiful terminal output
console = Console()

# Dictionary mapping ingredient codes to their names and emojis
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

# Emojis for trade status visualization
TRADE_EMOJIS = {
    'profit': '📈',
    'loss': '📉',
    'neutral': '➡️'
}

# Fee calculation constants
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

class CookieTrader:
    """
    Main class handling all trading operations and user interface.
    
    This class manages:
    - Database operations
    - Position tracking
    - Trade execution
    - Fee calculations
    - User interface
    """

    def __init__(self):
        """Initialize the CookieTrader with database connection."""
        self.db_path = 'trading.db'
        self.setup_database()
        
    def setup_database(self):
        """
        Initialize the database with required tables.
        
        Creates the following tables if they don't exist:
        - traders: Stores the number of traders and last update time
        - positions: Stores open and closed trading positions
        - trading_history: Stores completed trades with P/L information
        - portfolio: Stores current holdings of each ingredient
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create traders table for fee calculation
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS traders (
                    count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create positions table for tracking trades
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
            
            # Create trading history for completed trades
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
            
            # Create portfolio table for current holdings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    ingredient TEXT PRIMARY KEY,
                    total_quantity INTEGER DEFAULT 0,
                    average_price REAL DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Initialize traders count if table is empty
            cursor.execute('SELECT COUNT(*) FROM traders')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO traders (count) VALUES (0)')
            
            conn.commit()

    def get_current_fee(self):
        """
        Calculate the current trading fee percentage based on number of traders.
        
        The fee starts at BASE_FEE and is reduced by FEE_REDUCTION_PER_TRADER
        for each trader, but cannot go below 0%.
        
        Returns:
            float: The current fee percentage
        """
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
        """
        Add a new trading position to the database.
        
        Args:
            ingredient (str): The ingredient code (must exist in INGREDIENTS)
            quantity (int): Number of shares to buy
            price (float): Entry price per share
            comment (str, optional): Optional comment about the trade
        """
        if ingredient not in INGREDIENTS:
            console.print(f"[red]Invalid ingredient code: {ingredient}[/red]")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Add to positions table (for history)
            cursor.execute('''
                INSERT INTO positions (ingredient, quantity, entry_price, comment)
                VALUES (?, ?, ?, ?)
            ''', (ingredient, quantity, price, comment))
            
            # Update portfolio
            cursor.execute('''
                INSERT INTO portfolio (ingredient, total_quantity, average_price)
                VALUES (?, ?, ?)
                ON CONFLICT(ingredient) DO UPDATE SET
                    total_quantity = total_quantity + ?,
                    average_price = (average_price * total_quantity + ? * ?) / (total_quantity + ?),
                    last_updated = CURRENT_TIMESTAMP
            ''', (ingredient, quantity, price, quantity, price, quantity, quantity))
            
            conn.commit()
            
        # Display success message with trade details
        output = f"\n[green]📈 Position Opened:[/green]"
        output += f"\nIngredient: {quantity} {INGREDIENTS[ingredient]}"
        output += f"\nEntry Price: {format_price(price)}"
        if comment:
            output += f"\nComment: {comment}"
        console.print(output)
        self.wait_for_user()

    def close_position(self, ingredient, exit_price, comment=""):
        """
        Close or reduce a position for a specific ingredient.
        
        Args:
            ingredient (str): The ingredient code to close
            exit_price (float): Exit price per share
            comment (str, optional): Optional comment about the closing trade
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current portfolio position
            cursor.execute('SELECT total_quantity, average_price FROM portfolio WHERE ingredient = ?', (ingredient,))
            position = cursor.fetchone()
            
            if not position:
                console.print(f"[red]No position found for {ingredient}[/red]")
                self.wait_for_user()
                return
            
            total_quantity, avg_price = position
            
            # Ask for number of shares to sell
            sell_quantity = get_quantity("Enter number of shares to sell", total_quantity)
            if sell_quantity is None:
                console.print("[yellow]Operation cancelled[/yellow]")
                self.wait_for_user()
                return
            
            # Calculate profit/loss
            gross_pl = (exit_price - avg_price) * sell_quantity
            fee_percentage = self.get_current_fee()
            fee_amount = abs(gross_pl) * (fee_percentage / 100)
            net_pl = gross_pl - fee_amount
            
            # Update portfolio
            if sell_quantity == total_quantity:
                # Close the entire position
                cursor.execute('DELETE FROM portfolio WHERE ingredient = ?', (ingredient,))
            else:
                # Update the remaining quantity
                cursor.execute('''
                    UPDATE portfolio 
                    SET total_quantity = total_quantity - ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE ingredient = ?
                ''', (sell_quantity, ingredient))
            
            # Record in history
            cursor.execute('''
                INSERT INTO trading_history 
                (position_id, exit_price, profit_loss, fee_percentage, fee_amount, comment)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (None, exit_price, net_pl, fee_percentage, fee_amount, comment))
            
            conn.commit()
            
            pl_color = "green" if net_pl > 0 else "red"
            pl_emoji = "📈" if net_pl > 0 else "📉"
            output = f"\n[{pl_color}]{pl_emoji} Position Closed:[/{pl_color}]"
            output += f"\nIngredient: {ingredient} {INGREDIENTS[ingredient]}"
            output += f"\nShares Sold: {sell_quantity} of {total_quantity}"
            output += f"\nExit Price: {format_price(exit_price)}"
            output += f"\nGross P/L: {format_price(gross_pl)}"
            output += f"\nFee: {format_price(fee_amount)} @ {fee_percentage}%"
            output += f"\nNet P/L: {format_price(net_pl)}"
            if comment:
                output += f"\nComment: {comment}"
            console.print(output)
            self.wait_for_user()

    def get_position(self, position_id):
        """Get a position by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, ingredient, quantity, entry_price FROM positions WHERE id = ? AND status = "open"', (position_id,))
            return cursor.fetchone()

    def simulate_close(self, position_id=None):
        """
        Simulate closing a position with a hypothetical exit price.
        If position_id is provided, uses that position, otherwise prompts user.
        """
        if position_id is None:
            self.show_open_positions()
            position_id = custom_prompt("Enter position ID or ingredient code to simulate (or 'cancel' to exit)")
            if position_id is None:
                return
        
        # Try to find position by ID or ingredient code
        position = None
        if position_id.isdigit():
            position = self.get_position(int(position_id))
        else:
            # Try to find position by ingredient code
            ingredient_code = position_id.upper()
            positions = self.get_open_positions()
            for pos in positions:
                if pos['ingredient'] == ingredient_code:
                    position = pos
                    break
        
        if not position:
            console.print("[red]Invalid position ID or ingredient code![/red]")
            self.wait_for_user()
            return
            
        # Get exit price
        exit_price = custom_prompt("Enter exit price (or 'cancel' to exit)")
        if exit_price is None:
            return
            
        try:
            exit_price = float(exit_price)
        except ValueError:
            console.print("[red]Invalid price! Please enter a number.[/red]")
            self.wait_for_user()
            return
            
        # Calculate P/L
        entry_price = float(position['entry_price'])
        quantity = position['quantity']
        pl = (exit_price - entry_price) * quantity
        fee = abs(pl * self.get_current_fee())
        
        # Build output string
        output = f"""
[bold]Simulating Position Close[/bold]

Position Details:
• Ingredient: {position['ingredient']} {position['ingredient']}
• Quantity: {quantity} shares
• Entry Price: ${entry_price:.2f}
• Exit Price: ${exit_price:.2f}

Trade Summary:
• Potential P/L: ${pl:.2f}
• Fee ({self.get_current_fee()*100:.0f}%): ${fee:.2f}
• Net P/L: ${pl - fee:.2f}
"""
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
        self.wait_for_user()

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

    def sync_portfolio(self):
        """
        Synchronize the portfolio table with the positions table.
        This ensures the portfolio reflects the actual holdings based on all orders.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Clear the portfolio table
            cursor.execute('DELETE FROM portfolio')
            
            # Calculate current holdings from positions
            cursor.execute('''
                SELECT 
                    ingredient,
                    SUM(CASE WHEN status = 'open' THEN quantity ELSE 0 END) as total_quantity,
                    AVG(CASE WHEN status = 'open' THEN entry_price ELSE NULL END) as average_price
                FROM positions
                GROUP BY ingredient
                HAVING total_quantity > 0
            ''')
            
            # Insert or update portfolio entries
            for ingredient, quantity, avg_price in cursor.fetchall():
                cursor.execute('''
                    INSERT INTO portfolio (ingredient, total_quantity, average_price)
                    VALUES (?, ?, ?)
                ''', (ingredient, quantity, avg_price))
            
            conn.commit()

    def show_menu(self):
        """Display the main menu and handle user input."""
        while True:
            self.clear_screen()
            self.sync_portfolio()  # Sync portfolio before showing dashboard
            self.show_dashboard()
            self.show_menu_options()
            
            choice = Prompt.ask("\nSelect an option")
            
            if choice == "1":
                # Create ingredient choices display string
                ingredient_choices = "/".join(INGREDIENTS.keys())
                ingredient_display = "\n".join([f"{code} {INGREDIENTS[code]}" for code in INGREDIENTS.keys()])
                console.print(f"\nAvailable ingredients:\n{ingredient_display}")
                
                ingredient = custom_prompt(f"\nEnter ingredient code [{ingredient_choices}]")
                if ingredient is None:
                    continue
                    
                if ingredient.upper() not in INGREDIENTS:
                    console.print("[red]Invalid ingredient code![/red]")
                    continue
                
                quantity = get_quantity("Enter number of shares", 1000)  # Example max limit
                if quantity is None:
                    continue
                
                # Handle price input
                while True:
                    try:
                        price_str = custom_prompt("Enter entry price (e.g., 123.45 or $123.45)")
                        if price_str is None:
                            break
                        price = parse_price(price_str)
                        break
                    except ValueError as e:
                        if str(e) == "Operation cancelled":
                            break
                        console.print(f"[red]{str(e)}[/red]")
                
                if price_str is None:
                    continue
                
                # Get optional comment
                comment = get_comment("Add a comment (optional, press Enter to skip)")
                if comment is None:
                    continue
                
                self.add_position(ingredient.upper(), quantity, price, comment)
                
            elif choice == "2":
                self.show_portfolio()
                ingredient = custom_prompt("Enter ingredient code to close (or 'cancel' to exit)")
                if ingredient is None:
                    continue
                    
                if ingredient.upper() not in INGREDIENTS:
                    console.print("[red]Invalid ingredient code![/red]")
                    self.wait_for_user()
                    continue
                
                # Handle exit price input
                while True:
                    try:
                        price_str = custom_prompt("Enter exit price (e.g., 123.45 or $123.45)")
                        if price_str is None:
                            break
                        exit_price = parse_price(price_str)
                        break
                    except ValueError as e:
                        if str(e) == "Operation cancelled":
                            break
                        console.print(f"[red]{str(e)}[/red]")
                
                if price_str is None:
                    continue
                
                # Get optional comment
                comment = get_comment("Add a comment (optional, press Enter to skip)")
                if comment is None:
                    continue
                
                self.close_position(ingredient.upper(), exit_price, comment)
                
            elif choice == "3":
                self.simulate_close()
            elif choice == "4":
                self.simulate_trade()
            elif choice == "5":
                self.show_portfolio()
            elif choice == "6":
                self.show_trading_history()
                self.wait_for_user()
            elif choice == "7":
                self.update_traders()
            elif choice == "8":
                console.print("\n[yellow]Thank you for using Cookie Trading Manager![/yellow]")
                break
            else:
                console.print("[red]Invalid option![/red]")
                self.wait_for_user()

    def show_menu_options(self):
        """Display the menu options in a formatted panel."""
        menu_content = ""
        
        # Position Management (Green)
        menu_content += "\n[bold green]📊 Position Management[/bold green]"
        menu_content += "\n1. 📈 Open New Position"
        menu_content += "\n2. 📉 Close Position"
        menu_content += "\n3. 🔮 Simulate Position Close"
        menu_content += "\n4. 🎯 Simulate Complete Trade"
        
        # Analysis Tools (Blue)
        menu_content += "\n\n[bold blue]📈 Analysis Tools[/bold blue]"
        menu_content += "\n5. 📋 View Portfolio"
        menu_content += "\n6. 📜 Trading History"
        
        # Settings & System (Yellow)
        menu_content += "\n\n[bold yellow]⚙️ Settings & System[/bold yellow]"
        menu_content += "\n7. 👥 Update Traders Count"
        menu_content += "\n[bold red]8. ❌ Exit Program[/bold red]"
        
        menu_panel = Panel(
            menu_content,
            title="[bold]Available Actions[/bold]",
            border_style="cyan"
        )
        console.print(menu_panel)

    def show_portfolio(self):
        """Display current portfolio holdings."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ingredient, total_quantity, average_price
                FROM portfolio
                WHERE total_quantity > 0
                ORDER BY ingredient
            ''')
            holdings = cursor.fetchall()
            
            if not holdings:
                console.print("[yellow]No holdings in portfolio[/yellow]")
            else:
                table = Table(title="Current Portfolio", box=box.ROUNDED)
                table.add_column("Ingredient", style="magenta")
                table.add_column("Total Shares", justify="right")
                table.add_column("Average Price", justify="right")
                table.add_column("Total Value", justify="right")
                
                for holding in holdings:
                    ingredient, quantity, avg_price = holding
                    total_value = quantity * avg_price
                    table.add_row(
                        f"{ingredient} {INGREDIENTS[ingredient]}",
                        str(quantity),
                        format_price(avg_price),
                        format_price(total_value)
                    )
                
                console.print(table)
        
        self.wait_for_user()

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    trader = CookieTrader()
    trader.show_menu() 