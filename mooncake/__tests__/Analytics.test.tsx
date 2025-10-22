import { render, waitFor } from '@testing-library/react';
import Analytics from '@/components/Analytics';
import { usePathname } from 'next/navigation';
import { logEvent } from 'firebase/analytics';

// Mock the next/navigation module
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}));

// Mock the firebase/analytics module
jest.mock('firebase/analytics', () => ({
  logEvent: jest.fn(),
  getAnalytics: jest.fn(),
  isSupported: jest.fn(() => Promise.resolve(true)),
}));

// Mock the lib/firebase module
jest.mock('@/lib/firebase', () => ({
  analytics: Promise.resolve({}), // Mock the analytics promise
}));

describe('Analytics component', () => {
  beforeEach(() => {
    (logEvent as jest.Mock).mockClear();
  });

  it('should log a page_view event on initial render', async () => {
    (usePathname as jest.Mock).mockReturnValue('/initial-path');

    render(<Analytics />);

    await waitFor(() => {
      expect(logEvent).toHaveBeenCalledWith(expect.any(Object), 'page_view', {
        page_path: '/initial-path',
      });
    });
  });

  it('should log a page_view event when the path changes', async () => {
    (usePathname as jest.Mock).mockReturnValue('/initial-path');
    const { rerender } = render(<Analytics />);

    await waitFor(() => {
      expect(logEvent).toHaveBeenCalledWith(expect.any(Object), 'page_view', {
        page_path: '/initial-path',
      });
    });

    // Change the path
    (usePathname as jest.Mock).mockReturnValue('/new-path');
    rerender(<Analytics />);

    await waitFor(() => {
      expect(logEvent).toHaveBeenCalledWith(expect.any(Object), 'page_view', {
        page_path: '/new-path',
      });
    });

    expect(logEvent).toHaveBeenCalledTimes(2);
  });
});
