"""Utility functions for formatting data."""

from rich.prompt import Prompt
from rich.console import Console

console = Console()

def custom_prompt(prompt_text, choices=None, default="", show_choices=True):
    """
    Custom prompt function that handles cancel functionality consistently.
    
    Args:
        prompt_text (str): The prompt to display
        choices (list, optional): List of valid choices
        default (str, optional): Default value if user just presses Enter
        show_choices (bool, optional): Whether to show available choices
        
    Returns:
        str: User input, or None if cancelled
    """
    # Add cancel option to choices if provided
    if choices is not None:
        choices = list(choices) + ['cancel']
    
    # Add cancel hint to prompt
    if 'cancel' not in prompt_text.lower():
        prompt_text = f"{prompt_text} (or 'cancel' to exit)"
    
    try:
        result = Prompt.ask(prompt_text, choices=choices, default=default, show_choices=show_choices)
        if result.lower() == 'cancel':
            console.print("[yellow]Operation cancelled[/yellow]")
            return None
        return result
    except Exception as e:
        if "invalid choice" in str(e).lower():
            console.print("[red]Invalid input![/red]")
        return None

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
    if price_str is None:  # Handle cancelled input
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
    comment = custom_prompt(prompt_text)
    if comment is None:
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
        quantity_str = custom_prompt(f"{prompt} (max {max_quantity}, 'max'/'all')")
        if quantity_str is None:
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