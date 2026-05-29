import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Navbar from './Navbar'

describe('Navbar', () => {
  it('randează brand-ul și linkurile principale', () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    )

    expect(screen.getByText('FindMyJob')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Find Jobs' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Upload CV' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Log out' })).toBeInTheDocument()
  })
})