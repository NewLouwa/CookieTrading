"""Utility functions for formatting data."""

from rich.prompt import Prompt
from rich.console import Console

console = Console()

def parse_price(price_str):
    """
    Parse a price string into a float.
    
    Args:
        price_str (str): Price string (e.g., "123.45" or "$123.45")
        
    Returns:
        float: Parsed price value
        
    Raises:
        ValueError: If the price string is invalid
    """
    if price_str.lower() == 'cancel':
        raise ValueError("Operation cancelled")
        
    # Remove currency symbol and whitespace
    price_str = price_str.replace('$', '').strip()
    
    try:
        return float(price_str)
    except ValueError:
        raise ValueError("Invalid price format. Enter a number (e.g., 123.45 or $123.45)")

def format_price(price):
    """Format a price with currency symbol and 2 decimal places."""
    return f"${price:.2f}"

def get_comment(prompt_text, max_length=500):
    """
    Get an optional comment from the user.
    
    Args:
        prompt_text (str): The prompt to display
        max_length (int): Maximum length of the comment
        
    Returns:
        str: The comment, or None if cancelled
    """
    comment = Prompt.ask(prompt_text, default="")
    if comment.lower() == 'cancel':
        return None
    if comment:
        return comment[:max_length]
    return ""

def parse_quantity(quantity_str, max_quantity):
    """Parse quantity input, accepting 'max', 'all', or a number."""
    if not quantity_str:
        return None
    
    # Check for max/all keywords (case-insensitive)
    if quantity_str.lower() in ['max', 'all']:
        return max_quantity
    
    # Try to parse as number
    try:
        quantity = int(quantity_str)
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        if quantity > max_quantity:
            raise ValueError(f"Cannot exceed maximum quantity of {max_quantity}")
        return quantity
    except ValueError as e:
        if "invalid literal for int()" in str(e):
            raise ValueError("Please enter a number or 'max'/'all'")
        raise

def get_quantity(prompt, max_quantity):
    """
    Get a quantity from the user with validation.
    
    Args:
        prompt (str): The prompt text
        max_quantity (int): Maximum allowed quantity
        
    Returns:
        int: The validated quantity, or None if cancelled
    """
    while True:
        quantity_str = Prompt.ask(f"{prompt} (max {max_quantity}, 'max'/'all', or 'cancel' to exit)")
        
        if quantity_str.lower() == 'cancel':
            return None
            
        if quantity_str.lower() in ['max', 'all']:
            return max_quantity
            
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            if quantity > max_quantity:
                raise ValueError(f"Quantity cannot exceed {max_quantity}")
            return quantity
        except ValueError as e:
            console.print(f"[red]{str(e)}[/red]") 