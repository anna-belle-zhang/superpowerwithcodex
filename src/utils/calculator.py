"""Basic arithmetic helper functions."""


def add(a: float, b: float) -> float:
    """Return the sum of ``a`` and ``b``."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the result of subtracting ``b`` from ``a``."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of ``a`` and ``b``."""
    return a * b


def divide(a: float, b: float) -> float:
    """Return ``a`` divided by ``b``; raise ``ValueError`` if ``b`` is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
