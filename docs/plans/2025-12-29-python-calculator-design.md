# Python Calculator Module - Design Document

**Date:** 2025-12-29
**Purpose:** Test codex-subagent-driven-development workflow with a simple Python module

## Overview

A minimal Python calculator module with four basic operations (add, subtract, multiply, divide) to demonstrate the complete TDD workflow using Codex subagents.

## Architecture and Module Structure

**File structure:**
```
src/utils/calculator.py          # Implementation
tests/utils/test_calculator.py   # pytest tests
```

**Module design:**
- Simple, functional design with four pure functions
- Each function takes two numeric arguments and returns a numeric result
- No state, no classes - pure functions only
- Type hints for clarity (`def add(a: float, b: float) -> float`)

**Dependencies:**
- Runtime: None (pure Python 3.8+)
- Testing: pytest only

**Rationale:**
Functional over object-oriented for simplicity, clear boundaries for TDD, and minimal ceremony. Mirrors the existing JavaScript example (`src/utils/math.js`) while following Python conventions.

## API Design

**Function signatures:**

```python
def add(a: float, b: float) -> float:
    """Add two numbers."""

def subtract(a: float, b: float) -> float:
    """Subtract b from a."""

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""

def divide(a: float, b: float) -> float:
    """Divide a by b. Raises ValueError if b is zero."""
```

**Design decisions:**
1. **Parameter types:** Accept `float` to handle both integers and decimals
2. **Return types:** Always return `float` for consistency
3. **Naming:** Clear, unambiguous function names
4. **Operation order:** `subtract(a, b)` returns `a - b`, `divide(a, b)` returns `a / b`
5. **Module exports:** All four functions are public

**Example usage:**
```python
from src.utils.calculator import add, divide

result = add(10, 5)          # 15.0
quotient = divide(10, 2)     # 5.0
```

## Error Handling

**Strategy:** Minimal and focused - only handle division by zero.

**Division by zero:**
```python
def divide(a: float, b: float) -> float:
    """Divide a by b. Raises ValueError if b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

**Why ValueError?**
- Explicit input validation (not catching runtime error)
- Clear intent: "invalid value provided"
- Easier to test: raise before calculation

**What we're NOT handling:**
- Type validation (Python's type system handles this)
- Overflow (Python handles arbitrarily large numbers)
- NaN/Infinity (let Python's float behavior handle edge cases)
- Invalid argument counts (Python raises TypeError automatically)

**YAGNI applied:** Handle the one error that matters, trust Python for everything else.

## Testing Strategy

**Test structure:**

```python
# tests/utils/test_calculator.py
import pytest
from src.utils.calculator import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0.1, 0.2) == pytest.approx(0.3)  # Handle float precision

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5

def test_multiply():
    assert multiply(4, 5) == 20
    assert multiply(-2, 3) == -6

def test_divide():
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

**Testing principles:**
1. One assertion per concept (multiple assertions OK for same behavior with different inputs)
2. Descriptive test names (`test_divide_by_zero` is self-documenting)
3. Float comparison using `pytest.approx()` for floating-point arithmetic
4. Error testing with `pytest.raises()` context manager and message matching

**TDD workflow:**
Each test will clearly FAIL first (RED), then PASS after Codex implements (GREEN). Pytest output makes this progression very visible.

## Task Breakdown for TDD Workflow

**Task 1: Project setup**
- Create directory structure: `src/utils/`, `tests/utils/`
- Create `__init__.py` files for proper Python packaging
- Create `pytest.ini` or `pyproject.toml` for pytest configuration
- Verify pytest can discover tests
- **Owner:** Claude (no Codex needed for setup)

**Task 2: Add and subtract operations**
- **RED:** Claude writes tests for `test_add()` and `test_subtract()`
- **GREEN:** Codex implements `add()` and `subtract()` in `calculator.py`
- **REFACTOR:** Claude reviews code

**Task 3: Multiply operation**
- **RED:** Claude writes test for `test_multiply()`
- **GREEN:** Codex implements `multiply()`
- **REFACTOR:** Claude reviews code

**Task 4: Divide operation with error handling**
- **RED:** Claude writes tests for `test_divide()` and `test_divide_by_zero()`
- **GREEN:** Codex implements `divide()` with error handling
- **REFACTOR:** Claude reviews code

**Grouping rationale:**
- Task 2 groups similar operations to demonstrate Codex handling multiple functions
- Tasks 3-4 are separate to show incremental development
- Task 4 includes error handling to test Codex handling exceptions

**File boundaries for Codex:**
- **Implement in:** `src/utils/calculator.py`
- **Read only:** `tests/utils/test_calculator.py`, `pytest.ini`, `__init__.py`

## Success Criteria

1. All tests pass (`pytest tests/utils/test_calculator.py`)
2. Code follows Python conventions (type hints, docstrings)
3. Clean TDD cycle demonstrated: RED → GREEN → REFACTOR
4. Code review identifies no critical issues
5. Codex respects file boundaries (doesn't modify test files)
6. Proper error handling for division by zero

## Next Steps

1. Create git worktree for isolated development
2. Write detailed implementation plan
3. Execute using codex-subagent-driven-development workflow
