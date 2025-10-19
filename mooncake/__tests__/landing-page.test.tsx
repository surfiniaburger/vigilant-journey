import '@testing-library/jest-dom'
import { render, screen, act } from '@testing-library/react'
import Page from '@/app/page'
import { AuthProvider } from '@/context/AuthContext'

// Mock the ProtectedLink component to simplify the test
jest.mock('@/components/ui/ProtectedLink', () => ({
  ProtectedLink: ({ href, children }: { href: string; children: React.ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('Landing Page', () => {
  it('renders the main heading and CTA button', async () => {
    await act(async () => {
      render(<AuthProvider><Page /></AuthProvider>)
    });
 
    const heading = screen.getByRole('heading', { name: /Welcome to Alora/i });
    expect(heading).toBeInTheDocument();

    const button = screen.getByRole('button', { name: /Launch Co-Pilot/i });
    expect(button).toBeInTheDocument();
  })
})
