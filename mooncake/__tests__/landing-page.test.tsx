import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import Page from '@/app/page'

// Mock the ProtectedLink component to simplify the test
jest.mock('@/components/ui/ProtectedLink', () => ({
  ProtectedLink: ({ href, children }: { href: string; children: React.ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));

describe('Landing Page', () => {
  it('renders the main heading and CTA button', () => {
    render(<Page />)
 
    const heading = screen.getByRole('heading', { name: /Welcome to Alora/i });
    expect(heading).toBeInTheDocument();

    const button = screen.getByRole('button', { name: /Launch Co-Pilot/i });
    expect(button).toBeInTheDocument();
  })
})
