import '@testing-library/jest-dom'
import { render } from '@testing-library/react'
import { Map } from '@/components/ui/map'

describe('Map', () => {
  it('renders correctly', () => {
    const { container } = render(<Map />)
    expect(container).toBeInTheDocument()
  })

  it('renders map unchanged', () => {
    const { container } = render(<Map />)
    expect(container).toMatchSnapshot()
  })
})
