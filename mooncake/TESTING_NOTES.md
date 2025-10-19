# Testing Notes for the Mooncake Project

This document contains a summary of the key considerations and steps taken to ensure a stable testing environment for this project. It is intended to be a guide for future developers (including my future self) to avoid common pitfalls and resolve testing issues efficiently.

## Running the Tests

To run the entire test suite, use the following command from the `mooncake` directory:

```bash
npm test
```

To update snapshots, run:

```bash
npm test -- -u
```

## Key Considerations for Writing Tests

### 1. Mocking `next/navigation`

Any component that uses the `useRouter` hook from `next/navigation` will require a mock for the `next/navigation` module in its corresponding test file. Without this, you will encounter an `invariant expected app router to be mounted` error.

**Example:**

```javascript
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));
```

### 2. Handling Asynchronous State Updates with `act`

When testing components that involve asynchronous state updates (e.g., fetching data, authentication), you may encounter the error `An update to ... inside a test was not wrapped in act(...)`. This typically happens when a state update occurs after the initial render.

To resolve this, wrap the `render` call (and any subsequent actions that trigger state updates) within an `async act` block. This ensures that all state updates are processed before making assertions.

**Example:**

```javascript
import { render, screen, act } from '@testing-library/react';

// ...

it('should render correctly', async () => {
  await act(async () => {
    render(<MyComponent />);
  });

  // Now you can safely make assertions
  expect(screen.getByText('Loaded!')).toBeInTheDocument();
});
```

### 3. Mocking Authentication (`useAuth`)

When testing components that rely on the `useAuth` hook, you must provide a mock implementation for the hook. The mocked user object should be structured to match the real user object as closely as possible, including any functions that the component might call, such as `getIdToken`.

**Example for an authenticated user:**

```javascript
jest.mock('@/context/AuthContext');

// ...

(useAuth as jest.Mock).mockReturnValue({
  user: { 
    getIdToken: () => Promise.resolve('dummy-token') 
  },
  loading: false,
});
```

### 4. Keeping Tests Aligned with UI Changes

Remember that tests are a reflection of the current state of your application. If you refactor a component or change its UI, the corresponding tests will likely need to be updated. For instance, the `map-page.test.tsx` initially failed because it was looking for a `chat-interface` component that had been replaced with a `VoiceButton`.

Always review failing tests after a code change to determine if the test is outdated or if it has caught a genuine regression.

### 5. Correctly Mocking `useAuth`

The `voice-controller.test.tsx` tests failed with the error `useAuth must be used within an AuthProvider`. This was because the `VoiceController` component uses the `useAuth` hook, but the test environment was not providing the `AuthProvider` context.

The solution was to mock the `useAuth` hook directly in the test file:

```javascript
jest.mock('@/context/AuthContext');

const useAuthMock = useAuth as jest.Mock;

// In a beforeEach or within a specific test:
useAuthMock.mockReturnValue({
  user: {
    getIdToken: async () => 'test-token',
  },
});
```

This provides the necessary context for the component to render without needing to wrap it in a real `AuthProvider`.

### 6. Handling `act(...)` warnings with `waitFor`

After mocking `useAuth`, the tests passed but showed `act(...)` warnings in the console. This was because the `useEffect` hook in `VoiceController` was causing state updates after the initial render.

To fix this, I used `waitFor` from `@testing-library/react` to wait for the UI to update before making assertions.

**Example:**

```javascript
import { render, screen, waitFor } from '@testing-library/react';

// ...

it('should render the idle state', async () => {
  render(<VoiceController />);

  await waitFor(() => {
    expect(screen.getByText('State: idle')).toBeInTheDocument();
  });
});
```

### 7. Avoiding Syntax Errors in Test Files

A simple mistake of wrapping the entire test file content in triple quotes (`'''`) caused a syntax error and test failure. This is a reminder to be careful with string literals, especially when generating or modifying code programmatically. Always double-check the syntax of the generated code.
