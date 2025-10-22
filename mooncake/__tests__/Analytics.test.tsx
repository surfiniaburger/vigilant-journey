import { render } from '@testing-library/react';
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
  it('should log a page_view event on initial render', async () => {
    (usePathname as jest.Mock).mockReturnValue('/initial-path');

    render(<Analytics />);

    // Wait for the async useEffect to complete
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(logEvent).toHaveBeenCalledWith(expect.any(Object), 'page_view', {
      page_path: '/initial-path',
    });
  });

  it('should log a page_view event when the path changes', async () => {
    (usePathname as jest.Mock).mockReturnValue('/initial-path');
    const { rerender } = render(<Analytics />);

    // Wait for the initial render's async useEffect to complete
    await new Promise(resolve => setTimeout(resolve, 0));

    // Change the path
    (usePathname as jest.Mock).mockReturnValue('/new-path');
    rerender(<Analytics />);

    // Wait for the re-render's async useEffect to complete
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(logEvent).toHaveBeenCalledWith(expect.any(Object), 'page_view', {
      page_path: '/new-path',
    });
  });
});
