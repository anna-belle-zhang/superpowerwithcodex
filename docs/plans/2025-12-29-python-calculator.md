---
execution-strategy: codex-subagents
created: 2025-12-29
codex-available: true
---

# Python Calculator Module Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:codex-subagent-driven-development to implement this plan task-by-task.

**Goal:** Build a minimal Python calculator module with TDD to test the codex-subagent-driven-development workflow.

**Architecture:** Four pure functions (add, subtract, multiply, divide) with type hints, pytest tests, and minimal error handling (division by zero only). Mirrors existing JavaScript example structure.

**Tech Stack:** Python 3.8+, pytest

---

## Task 1: Project Setup

**Files:**
- Create: `src/utils/__init__.py`
- Create: `tests/utils/__init__.py`
- Create: `pytest.ini`

**Step 1: Create directory structure**

```bash
mkdir -p src/utils tests/utils
```

**Step 2: Create __init__.py files**

Create `src/utils/__init__.py` (empty file for Python package):
```python
# Empty file - makes src/utils a Python package
```

Create `tests/utils/__init__.py` (empty file):
```python
# Empty file - makes tests/utils a Python package
```

**Step 3: Create pytest configuration**

Create `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**Step 4: Verify pytest can discover tests**

Run: `pytest --collect-only`
Expected: "collected 0 items" (no tests yet, but discovery works)

**Step 5: Commit setup**

```bash
git add src/utils/__init__.py tests/utils/__init__.py pytest.ini
git commit -m "Setup: Python project structure and pytest config"
```

---

## Task 2: Add and Subtract Operations

**Files:**
- Create: `tests/utils/test_calculator.py`
- Create: `src/utils/calculator.py`

### Step 1: Write the failing tests

Create `tests/utils/test_calculator.py`:
```python
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
```

### Step 2: Run tests to verify they fail

Run: `pytest tests/utils/test_calculator.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.utils.calculator'"

### Step 3: Write minimal implementation (CODEX TASK)

**Codex boundaries:**
- **Implement in:** `src/utils/calculator.py`
- **Read only:** `tests/utils/test_calculator.py`

Create `src/utils/calculator.py`:
```python
def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a.

    Args:
        a: Number to subtract from
        b: Number to subtract

    Returns:
        Difference of a and b
    """
    return a - b
```

### Step 4: Run tests to verify they pass

Run: `pytest tests/utils/test_calculator.py::test_add -v`
Expected: PASS

Run: `pytest tests/utils/test_calculator.py::test_subtract -v`
Expected: PASS

### Step 5: Commit

```bash
git add tests/utils/test_calculator.py src/utils/calculator.py
git commit -m "Feat: Add addition and subtraction operations"
```

---

## Task 3: Multiply Operation

**Files:**
- Modify: `tests/utils/test_calculator.py`
- Modify: `src/utils/calculator.py`

### Step 1: Write the failing test

Add to `tests/utils/test_calculator.py`:
```python
from src.utils.calculator import add, subtract, multiply


def test_multiply():
    """Test multiplication of two numbers."""
    assert multiply(4, 5) == 20
    assert multiply(-2, 3) == -6
    assert multiply(0, 10) == 0
```

### Step 2: Run test to verify it fails

Run: `pytest tests/utils/test_calculator.py::test_multiply -v`
Expected: FAIL with "ImportError: cannot import name 'multiply'"

### Step 3: Write minimal implementation (CODEX TASK)

**Codex boundaries:**
- **Implement in:** `src/utils/calculator.py`
- **Read only:** `tests/utils/test_calculator.py`

Add to `src/utils/calculator.py`:
```python
def multiply(a: float, b: float) -> float:
    """Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Product of a and b
    """
    return a * b
```

### Step 4: Run test to verify it passes

Run: `pytest tests/utils/test_calculator.py::test_multiply -v`
Expected: PASS

### Step 5: Commit

```bash
git add tests/utils/test_calculator.py src/utils/calculator.py
git commit -m "Feat: Add multiplication operation"
```

---

## Task 4: Divide Operation with Error Handling

**Files:**
- Modify: `tests/utils/test_calculator.py`
- Modify: `src/utils/calculator.py`

### Step 1: Write the failing tests

Add to `tests/utils/test_calculator.py`:
```python
from src.utils.calculator import add, subtract, multiply, divide


def test_divide():
    """Test division of two numbers."""
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5
    assert divide(0, 5) == 0


def test_divide_by_zero():
    """Test that division by zero raises ValueError."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

### Step 2: Run tests to verify they fail

Run: `pytest tests/utils/test_calculator.py::test_divide -v`
Expected: FAIL with "ImportError: cannot import name 'divide'"

Run: `pytest tests/utils/test_calculator.py::test_divide_by_zero -v`
Expected: FAIL with "ImportError: cannot import name 'divide'"

### Step 3: Write minimal implementation (CODEX TASK)

**Codex boundaries:**
- **Implement in:** `src/utils/calculator.py`
- **Read only:** `tests/utils/test_calculator.py`

Add to `src/utils/calculator.py`:
```python
def divide(a: float, b: float) -> float:
    """Divide a by b.

    Args:
        a: Numerator
        b: Denominator

    Returns:
        Quotient of a and b

    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### Step 4: Run tests to verify they pass

Run: `pytest tests/utils/test_calculator.py::test_divide -v`
Expected: PASS

Run: `pytest tests/utils/test_calculator.py::test_divide_by_zero -v`
Expected: PASS

### Step 5: Commit

```bash
git add tests/utils/test_calculator.py src/utils/calculator.py
git commit -m "Feat: Add division operation with error handling"
```

---

## Final Verification

**Step 1: Run all tests**

Run: `pytest tests/utils/test_calculator.py -v`
Expected: All 5 tests PASS

**Step 2: Verify code structure**

Run: `python -c "from src.utils.calculator import add, subtract, multiply, divide; print('All imports successful')"`
Expected: "All imports successful"

**Step 3: Manual smoke test**

```python
from src.utils.calculator import add, subtract, multiply, divide

assert add(2, 3) == 5
assert subtract(10, 3) == 7
assert multiply(4, 5) == 20
assert divide(10, 2) == 5

try:
    divide(1, 0)
    assert False, "Should have raised ValueError"
except ValueError as e:
    assert str(e) == "Cannot divide by zero"

print("✓ All manual tests passed")
```

---

## Success Criteria Checklist

- [ ] All pytest tests pass
- [ ] Code has type hints on all functions
- [ ] Code has docstrings on all functions
- [ ] Division by zero raises ValueError with correct message
- [ ] Clean git history with commits per task
- [ ] No test files were modified by Codex (boundary enforcement)
