# E2E Retry Task Plan

## Task 1: Implement GET /status endpoint

Implement `GET /status` in `src/server.js` to return:
- HTTP 200
- JSON body: `{ "status": "ok" }`

Unit tests: `npm test`
E2E: `npx playwright test`
