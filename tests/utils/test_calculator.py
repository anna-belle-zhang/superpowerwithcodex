import pytest
from src.utils.calculator import add, subtract, multiply, divide


def test_add():
    """Test addition of two numbers."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0.1, 0.2) == pytest.approx(0.3)


def test_subtract():
    """Test subtraction of two numbers."""
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5


def test_multiply():
    """Test multiplication of two numbers."""
    assert multiply(4, 5) == 20
    assert multiply(-2, 3) == -6
    assert multiply(0, 10) == 0


def test_divide():
    """Test division of two numbers."""
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5
    assert divide(0, 5) == 0


def test_divide_by_zero():
    """Test that division by zero raises ValueError."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
