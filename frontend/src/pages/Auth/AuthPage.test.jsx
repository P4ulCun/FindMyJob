import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import AuthPage from './AuthPage'

const renderAuth = () =>
  render(<MemoryRouter><AuthPage /></MemoryRouter>)

// Helper: butonul de submit (al doilea "Log in", nu tab-ul)
const getSubmitBtn = () => screen.getAllByRole('button', { name: /log in/i }).at(-1)

describe('AuthPage', () => {
  beforeEach(() => vi.restoreAllMocks())

  it('afișează formularul de login implicit fără câmpul Full name', () => {
    renderAuth()
    expect(getSubmitBtn()).toBeInTheDocument()
    expect(screen.queryByLabelText(/full name/i)).not.toBeInTheDocument()
  })

  it('afișează câmpul Full name după switch pe Register', () => {
    renderAuth()
    fireEvent.click(screen.getByRole('button', { name: /register/i }))
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
  })

  it('afișează eroarea primită de la server la login eșuat', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      json: async () => ({ detail: 'Invalid credentials.' }),
    })

    renderAuth()
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'wrong' } })
    fireEvent.click(getSubmitBtn())

    expect(await screen.findByText('Invalid credentials.')).toBeInTheDocument()
  })

  it('afișează eroare de rețea când fetch aruncă excepție', async () => {
    vi.spyOn(global, 'fetch').mockRejectedValue(new Error('Network down'))

    renderAuth()
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } })
    fireEvent.click(getSubmitBtn())

    expect(await screen.findByText('Could not connect to the server.')).toBeInTheDocument()
  })
})
