"""Tests for formatting utilities."""

import pytest
from src.utils.formatting import parse_price, format_price, get_comment

def test_parse_price():
    """Test price string parsing."""
    # Test valid price formats
    assert parse_price("123.45") == 123.45
    assert parse_price("$123.45") == 123.45
    assert parse_price("123") == 123.0
    assert parse_price("$123") == 123.0
    assert parse_price("0") == 0.0
    assert parse_price("$0") == 0.0
    assert parse_price("") == 0.0
    
    # Test invalid price formats
    with pytest.raises(ValueError):
        parse_price("abc")
    with pytest.raises(ValueError):
        parse_price("$abc")
    with pytest.raises(ValueError):
        parse_price("123.abc")

def test_format_price():
    """Test price formatting."""
    # Test positive prices
    assert format_price(123.45) == "$123.45"
    assert format_price(123) == "$123.00"
    assert format_price(0) == "$0.00"
    
    # Test negative prices (should show absolute value)
    assert format_price(-123.45) == "$123.45"
    assert format_price(-123) == "$123.00"
    assert format_price(-0) == "$0.00"

def test_get_comment():
    """Test comment input formatting."""
    # In non-interactive environment, should return empty string
    assert get_comment("Test prompt", max_length=500) == ""
    
    # Test comment exceeding limit
    long_comment = "a" * 600
    assert len(get_comment("Test prompt", max_length=500)) <= 500 