import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import MapPage from '@/app/map/page';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

jest.mock('@/context/AuthContext', () => ({
  useAuth: jest.fn(),
}));

jest.mock('@/components/ui/chat-interface', () => ({
  ChatInterface: () => <div data-testid="chat-interface">Chat Interface</div>,
}));

import { useAuth } from '@/context/AuthContext';

describe('Map Page', () => {
  it('shows a loading state while checking authentication', () => {
    (useAuth as jest.Mock).mockReturnValue({ user: null, loading: true });
    render(<MapPage />);
    expect(screen.getByText('Authenticating...')).toBeInTheDocument();
  });

  it('renders the chat interface for an authenticated user', () => {
    (useAuth as jest.Mock).mockReturnValue({
      user: { getIdToken: () => Promise.resolve('dummy-token') },
      loading: false,
    });
    render(<MapPage />);
    // We need to wait for the token and state update
    expect(screen.findByTestId('chat-interface')).toBeTruthy();
  });
});
