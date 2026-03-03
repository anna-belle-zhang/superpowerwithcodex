const { describe, it } = require('node:test');
const assert = require('node:assert');
const { greet } = require('../src/greet');

describe('greet', () => {
  it('returns Hello, World! when given World', () => {
    assert.strictEqual(greet('World'), 'Hello, World!');
  });
  it('returns Hello, Alice! when given Alice', () => {
    assert.strictEqual(greet('Alice'), 'Hello, Alice!');
  });
});
