import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import Page from '@/app/page'
 
describe('Page', () => {
  it('renders the main content', () => {
    render(<Page />)
 
    const listItem = screen.getByText(/Get started by editing/i)
 
    expect(listItem).toBeInTheDocument()
  })

  it('renders homepage unchanged', () => {
    const { container } = render(<Page />)
    expect(container).toMatchSnapshot()
  })
})
