import { test, expect } from '@playwright/test';

test.describe('Authenticated user', () => {
  test('should be redirected to the map page', async ({ page }) => {
    // Start from the home page.
    await page.goto('/');

    // Wait for navigation to the map page.
    await page.waitForURL('/map');

    // Assert that the current URL is the map page.
    await expect(page).toHaveURL('/map');
  });
});
