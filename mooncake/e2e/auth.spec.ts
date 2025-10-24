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

  test('should see the map page and be able to interact with it', async ({ page }) => {
    // Start directly from the map page, since the user is already authenticated.
    await page.goto('/map');

    // Wait for the "Authenticating..." message to disappear.
    await expect(page.getByText('Authenticating...')).not.toBeVisible();

    // Verify that the voice button is visible.
    const voiceButton = page.getByRole('button', { name: 'voice-button' });
    await expect(voiceButton).toBeVisible();

    // Click the voice button and verify the state changes.
    await voiceButton.click();
    await expect(voiceButton).toHaveAttribute('data-state', 'recording');
  });
});
