"""Utility functions for formatting data."""

from rich.prompt import Prompt
from rich.console import Console
from typing import Optional, Union, Callable, Any

console = Console()

def get_input(
    prompt: str,
    validator: Optional[Callable[[str], Any]] = None,
    error_message: Optional[str] = None,
    default: str = "",
    show_default: bool = True,
    show_cancel: bool = True
) -> Optional[Any]:
    """
    Get user input with validation and cancel support.
    
    Args:
        prompt (str): The prompt text to display
        validator (Callable, optional): Function to validate the input
        error_message (str, optional): Custom error message for validation failures
        default (str, optional): Default value if user just presses Enter
        show_default (bool, optional): Whether to show the default value in prompt
        show_cancel (bool, optional): Whether to show cancel option in prompt
        
    Returns:
        Any: The validated input value, or None if cancelled
    """
    # Add cancel option to prompt if enabled
    if show_cancel:
        prompt = f"{prompt} (or 'cancel' to exit)"
    
    while True:
        try:
            value = Prompt.ask(prompt, default=default, show_default=show_default)
            
            # Check for cancel
            if value.lower() == 'cancel':
                console.print("[yellow]Operation cancelled[/yellow]")
                return None
            
            # If no validator, return the raw input
            if validator is None:
                return value
            
            # Validate the input
            return validator(value)
            
        except ValueError as e:
            if error_message:
                console.print(f"[red]{error_message}[/red]")
            else:
                console.print(f"[red]{str(e)}[/red]")

def parse_price(price_str: str) -> float:
    """
    Parse a price string into a float.
    
    Args:
        price_str (str): Price string (e.g., "123.45" or "$123.45")
        
    Returns:
        float: Parsed price value
        
    Raises:
        ValueError: If the price string is invalid
    """
    # Remove currency symbol and whitespace
    price_str = price_str.replace('$', '').strip()
    
    try:
        return float(price_str)
    except ValueError:
        raise ValueError("Invalid price format. Enter a number (e.g., 123.45 or $123.45)")

def format_price(price: float) -> str:
    """Format a price with currency symbol and 2 decimal places."""
    return f"${price:.2f}"

def get_comment(prompt_text: str, max_length: int = 500) -> Optional[str]:
    """
    Get an optional comment from the user.
    
    Args:
        prompt_text (str): The prompt to display
        max_length (int): Maximum length of the comment
        
    Returns:
        str: The comment, or None if cancelled
    """
    comment = get_input(prompt_text, default="")
    if comment is None:
        return None
    if comment:
        return comment[:max_length]
    return ""

def get_quantity(prompt: str, max_quantity: int) -> Optional[int]:
    """
    Get a quantity from the user with validation.
    
    Args:
        prompt (str): The prompt text
        max_quantity (int): Maximum allowed quantity
        
    Returns:
        int: The validated quantity, or None if cancelled
    """
    def validate_quantity(value: str) -> int:
        if value.lower() in ['max', 'all']:
            return max_quantity
            
        quantity = int(value)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > max_quantity:
            raise ValueError(f"Quantity cannot exceed {max_quantity}")
        return quantity
    
    return get_input(
        f"{prompt} (max {max_quantity}, 'max'/'all'",
        validator=validate_quantity,
        error_message="Please enter a valid number, 'max', 'all', or 'cancel'"
    ) 