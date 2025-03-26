"""Cookie Trading Manager main application."""

from rich.console import Console
from prompt_toolkit import PromptSession
from src.utils.database import setup_database
from src.views.dashboard import show_dashboard
from src.views.tables import show_open_positions, show_trading_history
from src.controllers.trader import TraderController

console = Console()
session = PromptSession()

def show_menu():
    """Display the main menu and handle user input."""
    trader = TraderController()
    
    while True:
        console.clear()
        console.print("[bold cyan]🍪 Cookie Trading Manager[/bold cyan]")
        
        # Show dashboard at the top
        show_dashboard()
        
        console.print("\n1. 📈 Add Position")
        console.print("2. 📉 Close Position")
        console.print("3. 🔮 Simulate Close")
        console.print("4. 📊 Show Open Positions")
        console.print("5. 📜 Show Trading History")
        console.print("6. 👥 Update Traders Count")
        console.print("7. ❌ Exit")
        
        choice = session.prompt("\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "7"])
        
        if choice == "1":
            trader.add_position()
            
        elif choice == "2":
            trader.close_position()
            
        elif choice == "3":
            trader.simulate_close()
            
        elif choice == "4":
            show_open_positions()
            
        elif choice == "5":
            show_trading_history()
            
        elif choice == "6":
            try:
                count = int(session.prompt("Enter new trader count"))
                trader.update_traders(count)
            except ValueError:
                console.print("[red]Please enter a valid number![/red]")
            
        elif choice == "7":
            console.print("[yellow]Goodbye! 👋[/yellow]")
            break

def main():
    """Main application entry point."""
    try:
        # Initialize database
        setup_database()
        
        # Start the application
        show_menu()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! 👋[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

if __name__ == "__main__":
    main() 