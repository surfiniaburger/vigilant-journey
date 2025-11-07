
import { test, expect } from '@playwright/test';

test('WebSocket connection sends Authorization header for logged-in user', async ({ page }) => {
  // Mock Firebase user in local storage
  await page.addInitScript(() => {
    window.localStorage.setItem('firebase:auth:781283643118:studio-l13dd:[DEFAULT]', JSON.stringify({
      "v": "2.1.2",
      "p": {
        "u": "test-uid",
        "e": "test@example.com",
        "a": "test-uid",
        "s": "test-token"
      },
      "s": null
    }));
  });

  let wsUrl;
  let headers;

  // Listen for the WebSocket request and capture its URL and headers
  page.on('request', request => {
    // We can't directly inspect WebSocket headers after the handshake starts with page.on('websocket').
    // Instead, we inspect the initial HTTP/S upgrade request.
    if (request.url().startsWith('ws')) {
        wsUrl = request.url();
        headers = request.headers();
    }
  });

  // Go to the home page
  await page.goto('http://localhost:3000');

  // For a logged-in user, the app should automatically redirect to the map
  await page.waitForURL('**/map', { timeout: 10000 });

  // Assert that the WebSocket was created
  expect(wsUrl).toBeDefined();

  // Expect the WebSocket URL to not contain the token
  expect(wsUrl).not.toContain('token=');

  // Expect the headers to contain the Authorization header
  // Note: Playwright headers are lowercase.
  expect(headers).toHaveProperty('authorization', 'Bearer test-token');
});
