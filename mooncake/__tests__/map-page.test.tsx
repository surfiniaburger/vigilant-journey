import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import MapPage from '@/app/map/page';
import { useAuth } from '@/context/AuthContext';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

jest.mock('@/context/AuthContext');

// Mock the useAudio hook to prevent it from running in tests
jest.mock('@/lib/use-audio', () => ({
  useAudio: () => ({}),
}));

describe('Map Page', () => {
  it('shows a loading state while checking authentication', () => {
    (useAuth as jest.Mock).mockReturnValue({ user: null, loading: true });
    render(<MapPage />);
    expect(screen.getByText('Authenticating...')).toBeInTheDocument();
  });

  it('renders the map and voice button for an authenticated user', async () => {
    (useAuth as jest.Mock).mockReturnValue({
      user: { getIdToken: () => Promise.resolve('dummy-token') },
      loading: false,
    });

    render(<MapPage />);

    // Use waitFor to handle asynchronous rendering and state updates
    await waitFor(() => {
      // The map is rendered via a div with a specific style
      const mapElement = screen.getByRole('button', { name: 'Voice Button' });
      expect(mapElement).toBeInTheDocument();
    });
  });
});