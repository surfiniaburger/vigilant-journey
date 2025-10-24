
import { test as setup, expect } from '@playwright/test';
import { mockFirebaseAuthentication } from './mock-auth';

const authFile = 'e2e/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Mock Firebase authentication
  await mockFirebaseAuthentication(page);

  // Go to the home page
  await page.goto('/');

  // Click the button to trigger the sign-in process
  await page.getByRole('button', { name: 'Launch Co-Pilot' }).click();

  // Wait for the redirect to the map page
  await page.waitForURL('/map');

  // Assert that we are on the map page
  await expect(page).toHaveURL('/map');

  // Save the authentication state
  await page.context().storageState({ path: authFile });
});
