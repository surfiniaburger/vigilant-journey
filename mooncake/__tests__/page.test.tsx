import '@testing-library/jest-dom'
import { render, screen, act } from '@testing-library/react'
import Page from '@/app/page'
import { AuthProvider } from '@/context/AuthContext'

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));
 
describe('Page', () => {
  it('renders the main content', async () => {
    await act(async () => {
      render(<AuthProvider><Page /></AuthProvider>)
    });
 
    const button = screen.getByRole('button')
 
    expect(button).toBeInTheDocument()
  })

  it('renders homepage unchanged', async () => {
    let container
    await act(async () => {
      const { container: c } = render(<AuthProvider><Page /></AuthProvider>)
      container = c
    });
    expect(container).toMatchSnapshot()
  })
})
