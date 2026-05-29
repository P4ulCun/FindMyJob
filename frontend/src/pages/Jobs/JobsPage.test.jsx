import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import JobsPage from './JobsPage'
import { apiFetch } from '../../utils/api'

// Mock complet al modulului de API — zero request-uri reale
vi.mock('../../utils/api', () => ({
  apiFetch: vi.fn(),
  authHeaders: vi.fn(() => ({})),
}))

// Cache-ul folosește localStorage; îl izolăm ca testul să fie determinist
vi.mock('../../utils/jobsSearchCache', () => ({
  loadCachedSearch: vi.fn(() => ({ jobs: [], message: '', searched: false })),
  saveCachedSearch: vi.fn(),
  clearCachedSearch: vi.fn(),
}))

describe('JobsPage', () => {
  beforeEach(() => vi.clearAllMocks())

  it('afișează joburile întoarse de API după click pe Search', async () => {
    apiFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        jobs: [
          {
            title: 'Senior Python Developer',
            company: 'Acme',
            source: 'RemoteOK',
            score: 88,
            summary: 'Potrivire bună',
            url: 'https://example.com/1',
          },
        ],
      }),
    })

    render(
      <MemoryRouter>
        <JobsPage />
      </MemoryRouter>
    )

    fireEvent.click(screen.getByRole('button', { name: /search jobs/i }))

    expect(await screen.findByText('Senior Python Developer')).toBeInTheDocument()
    expect(apiFetch).toHaveBeenCalledWith('/api/jobs/search/', { method: 'POST' })
  })
})