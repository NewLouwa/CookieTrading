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