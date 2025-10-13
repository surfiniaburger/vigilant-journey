import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { Badge } from '@/components/ui/badge'
 
describe('Badge', () => {
  it('renders with default variant', () => {
    render(<Badge>Default Badge</Badge>)
    const badgeElement = screen.getByText('Default Badge')
    expect(badgeElement).toBeInTheDocument()
    expect(badgeElement).toHaveClass('bg-primary')
  })
 
  it('renders with destructive variant', () => {
    render(<Badge variant="destructive">Destructive Badge</Badge>)
    const badgeElement = screen.getByText('Destructive Badge')
    expect(badgeElement).toBeInTheDocument()
    expect(badgeElement).toHaveClass('bg-destructive')
  })
 
  it('renders with outline variant', () => {
    render(<Badge variant="outline">Outline Badge</Badge>)
    const badgeElement = screen.getByText('Outline Badge')
    expect(badgeElement).toBeInTheDocument()
    expect(badgeElement).toHaveClass('text-foreground')
  })
});
