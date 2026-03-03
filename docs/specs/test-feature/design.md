# Test Feature Design

## Architecture
A single `greeter` module with a pure function interface. No external dependencies, no side effects.

## Components
- **`greeter`** — accepts a `name` string, returns a greeting string. Handles the empty-name case internally.

## Data Flow
```
caller → greeter(name) → greeting string
```
- Input: `name` (string)
- Output: greeting string
- No async, no I/O

## Error Handling
- Empty string input → returns a default greeting (e.g., "Hello, stranger!")
- No exceptions raised for any string input

## Dependencies
- None — standalone module, no external packages required
