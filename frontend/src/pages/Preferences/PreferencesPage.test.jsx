import { render, screen, fireEvent } from '@testing-library/react'
import PreferencesPage from './PreferencesPage'

vi.mock('../../utils/api', () => ({
  authHeaders: vi.fn(() => ({ Authorization: 'Bearer test' })),
}))

const PREFS = {
  job_title: 'Python Developer',
  location: 'Remote',
  work_type: 'remote',
  seniority: 'mid',
  source_remoteok: true,
  source_arbeitnow: true,
  source_hn: false,
  digest_frequency: 'off',
}

describe('PreferencesPage', () => {
  beforeEach(() => vi.restoreAllMocks())

  it('randează formularul cu datele încărcate', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => PREFS,
    })

    render(<PreferencesPage />)

    expect(await screen.findByDisplayValue('Python Developer')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Remote')).toBeInTheDocument()
  })

  it('afișează succes după salvare reușită', async () => {
    vi.spyOn(global, 'fetch')
      .mockResolvedValueOnce({ ok: true, json: async () => PREFS })
      .mockResolvedValueOnce({ ok: true, json: async () => PREFS })

    render(<PreferencesPage />)
    await screen.findByDisplayValue('Python Developer')

    fireEvent.click(screen.getByRole('button', { name: /save/i }))

    expect(await screen.findByText('Preferences saved successfully.')).toBeInTheDocument()
  })

  it('nu permite dezactivarea ultimei surse active', async () => {
    const prefsOneSrc = { ...PREFS, source_remoteok: true, source_arbeitnow: false, source_hn: false }
    vi.spyOn(global, 'fetch').mockResolvedValue({ ok: true, json: async () => prefsOneSrc })

    render(<PreferencesPage />)
    await screen.findByDisplayValue('Python Developer')

    const switches = screen.getAllByRole('switch')
    const disabledSwitch = switches.find(s => s.disabled)
    expect(disabledSwitch).toBeDefined()
  })
})
