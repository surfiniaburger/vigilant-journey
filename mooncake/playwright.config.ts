import { defineConfig, devices } from '@playwright/test';

const authFile = 'e2e/.auth/user.json';

export default defineConfig({
  testDir: './e2e',
  testIgnore: '**/__tests__/**',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    // Setup project
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'Desktop Chrome',
      use: {
        ...devices['Desktop Chrome'],
        // Use prepared auth state.
        storageState: authFile,
      },
      dependencies: ['setup'],
    },
    // {
    //   name: 'Desktop Firefox',
    //   use: {
    //     ...devices['Desktop Firefox'],
    //     storageState: authFile,
    //   },
      // dependencies: ['setup'],
    // },
    // {
    //   name: 'Desktop Safari',
    //   use: {
    //     ...devices['Desktop Safari'],
    //     storageState: authFile,
    //   },
      // dependencies: ['setup'],
    // },
    // Test against mobile viewports.
    {
      name: 'Mobile Chrome',
      use: {
        ...devices['Pixel 5'],
        storageState: authFile,
      },
      dependencies: ['setup'],
    },
    {
      name: 'Mobile Safari',
      use: {
        ...devices['iPhone 12'],
        storageState: authFile,
      },
      dependencies: ['setup'],
    },
  ],
});
