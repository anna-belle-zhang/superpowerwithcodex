const { divide } = require('../src/calculator');

test('divides two numbers', () => {
  expect(divide(10, 2)).toBe(5);
});

test('returns float', () => {
  expect(divide(7, 2)).toBe(3.5);
});

test('throws DivisionByZeroError for 1/0', () => {
  expect(() => divide(1, 0)).toThrow('DivisionByZeroError');
});

test('throws DivisionByZeroError for 0/0', () => {
  expect(() => divide(0, 0)).toThrow('DivisionByZeroError');
});
