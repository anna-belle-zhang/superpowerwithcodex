const { evaluate } = require('../src/paradox');

test('must return true', () => {
  expect(evaluate()).toBe(true);
});

test('must return false', () => {
  expect(evaluate()).toBe(false);
});
