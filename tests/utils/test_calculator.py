import pytest
from src.utils.calculator import add, subtract


def test_add():
    """Test addition of two numbers."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0.1, 0.2) == pytest.approx(0.3)


def test_subtract():
    """Test subtraction of two numbers."""
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5
