"""Utility functions for formatting data."""

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

def get_comment(prompt_text, max_length=500):
    """Get optional comment from user."""
    try:
        from prompt_toolkit import PromptSession
        session = PromptSession()
        comment = session.prompt(prompt_text, default="")
        if comment:
            return comment[:max_length]
        return ""
    except Exception:
        # Return empty string in non-interactive environments
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
    """Get quantity from user with support for max/all and cancellation."""
    while True:
        try:
            quantity_str = Prompt.ask(f"{prompt} (max {max_quantity}, 'max'/'all', or 'cancel' to exit)")
            if quantity_str.lower() == 'cancel':
                return None
            quantity = parse_quantity(quantity_str, max_quantity)
            return quantity
        except ValueError as e:
            console.print(f"[red]{str(e)}[/red]") 