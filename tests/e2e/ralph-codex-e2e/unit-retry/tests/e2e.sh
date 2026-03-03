#!/bin/bash
set -e
node -e "
const { divide } = require('./src/calculator');
const result = divide(10, 2);
if (result !== 5) { console.error('E2E FAIL'); process.exit(1); }
console.log('E2E PASS: 10/2 =', result);
"
