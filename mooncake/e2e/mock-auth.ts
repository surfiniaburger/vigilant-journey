
import { Page } from '@playwright/test';
import { User } from 'firebase/auth';

// A mock Firebase user object
export const mockUser: User = {
  uid: 'mock-uid',
  email: 'mock.user@example.com',
  displayName: 'Mock User',
  photoURL: null,
  emailVerified: true,
  isAnonymous: false,
  metadata: {},
  providerData: [],
  refreshToken: 'mock-refresh-token',
  tenantId: null,
  delete: async () => {},
  phoneNumber: null,
  providerId: 'mock-provider-id',
  // Add other methods and properties as needed, with mock implementations
  getIdToken: async () => 'mock-id-token',
  getIdTokenResult: async () => ({
    token: 'mock-id-token',
    // Add other properties as needed
  } as any),
  reload: async () => {},
  toJSON: () => ({}),
} as User;

/**
 * Mocks the Firebase authentication flow in the browser.
 * This function should be called in a Playwright test before navigating to the page.
 * It intercepts Firebase's `signInWithPopup` and `onAuthStateChanged` calls.
 *
 * @param page The Playwright page object.
 */
export async function mockFirebaseAuthentication(page: Page) {
  // Mock the network call that Firebase Auth makes to validate the user.
  // This is a more robust method than intercepting and modifying JS files.
  await page.route(
    'https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo',
    (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          users: [
            {
              localId: 'mock-uid',
              email: 'mock.user@example.com',
              displayName: 'Mock User',
              photoUrl: null,
              emailVerified: true,
              providerUserInfo: [
                {
                  providerId: 'password',
                  rawId: 'mock.user@example.com',
                  email: 'mock.user@example.com',
                  displayName: 'Mock User',
                  photoUrl: null,
                },
              ],
            },
          ],
        }),
      });
    }
  );

  // Mock the onAuthStateChanged behavior by directly manipulating the Firebase SDK
  await page.addInitScript(() => {
    const mockUser = {
      uid: 'mock-uid',
      email: 'mock.user@example.com',
      displayName: 'Mock User',
      photoURL: null,
      emailVerified: true,
      isAnonymous: false,
      metadata: {},
      providerData: [],
      getIdToken: async () => 'mock-id-token',
      getIdTokenResult: async () => ({ token: 'mock-id-token' }),
      reload: async () => {},
      toJSON: () => ({}),
    };

    // This function will be called by the Firebase SDK
    const mockOnAuthStateChanged = (auth: any, callback: (user: any) => void) => {
      callback(mockUser);
      return () => {}; // Return an unsubscribe function
    };

    // When the app tries to get the auth object, we give it one with a mocked onAuthStateChanged
    (window as any).mockGetAuth = (realGetAuth: any) => {
        return (...args: any[]) => {
            const auth = realGetAuth(...args);
            auth.onAuthStateChanged = (callback: (user: any) => void) => mockOnAuthStateChanged(auth, callback);
            return auth;
        };
    };
  });

  // Intercept a known part of the app's code to apply the mock
  await page.route('**/_next/static/chunks/main-*.js', async (route) => {
    const response = await route.fetch();
    let body = await response.text();
    // This is still a bit of a hack, but it's more targeted.
    // We're replacing the getAuth import with our mocked version.
    body = body.replace(
      /import\(([^)]+)\)"firebase\/auth"/,
      'import($1)"firebase/auth").then(mod => ({ ...mod, getAuth: window.mockGetAuth(mod.getAuth) }))'
    );
    await route.fulfill({ response, body });
  });
}
