const request = require('supertest');
const app = require('../src/server');

test('GET /status returns 200', async () => {
  const res = await request(app).get('/status');
  expect(res.status).toBe(200);
  expect(res.body).toHaveProperty('status');
});
