import { test, expect } from '@playwright/test';

test('GET /status returns X-Version: 1 header', async ({ request }) => {
  const response = await request.get('/status');
  expect(response.ok()).toBeTruthy();
  const headers = response.headers();
  expect(headers['x-version']).toBe('1');
});
