import { render, screen } from '@testing-library/react'
import ApplicationsPage from './ApplicationsPage'
import { apiFetch } from '../../utils/api'

vi.mock('../../utils/api', () => ({
  apiFetch: vi.fn(),
  authHeaders: vi.fn(() => ({})),
}))

describe('ApplicationsPage', () => {
  beforeEach(() => vi.clearAllMocks())

  it('afișează starea goală când nu există interacțiuni', async () => {
    apiFetch.mockResolvedValue({ ok: true, json: async () => ({ interactions: [] }) })

    render(<ApplicationsPage />)

    expect(await screen.findByText(/haven't tracked any jobs/i)).toBeInTheDocument()
  })

  it('grupează joburile pe coloane Applied / Saved / Rejected', async () => {
    apiFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        interactions: [
          { id: 1, status: 'applied',  job_title: 'Python Dev',   job_company: 'Acme',  job_location: 'Remote', job_url: 'https://x.com', updated_at: '2024-01-01' },
          { id: 2, status: 'saved',    job_title: 'React Dev',    job_company: 'Beta',  job_location: 'Berlin', job_url: 'https://y.com', updated_at: '2024-01-02' },
          { id: 3, status: 'rejected', job_title: 'Data Analyst', job_company: 'Gamma', job_location: 'Paris',  job_url: 'https://z.com', updated_at: '2024-01-03' },
        ],
      }),
    })

    render(<ApplicationsPage />)

    expect(await screen.findByText('Python Dev')).toBeInTheDocument()
    expect(screen.getByText('React Dev')).toBeInTheDocument()
    expect(screen.getByText('Data Analyst')).toBeInTheDocument()
    expect(screen.getByText(/applied/i)).toBeInTheDocument()
    expect(screen.getByText(/saved/i)).toBeInTheDocument()
    expect(screen.getByText(/rejected/i)).toBeInTheDocument()
  })

  it('afișează eroare când API-ul întoarce status non-ok', async () => {
    apiFetch.mockResolvedValue({ ok: false, json: async () => ({}) })

    render(<ApplicationsPage />)

    expect(await screen.findByText(/failed to fetch/i)).toBeInTheDocument()
  })
})
