const STORAGE_KEY = 'findmyjob_jobs_search_cache'

/** @type {{ jobs: unknown[], message: string, searched: boolean } | null} */
let memoryCache = null

function defaults() {
  return { jobs: [], message: '', searched: false }
}

/**
 * @returns {{ jobs: unknown[], message: string, searched: boolean }}
 */
export function loadCachedSearch() {
  if (memoryCache) {
    return {
      jobs: Array.isArray(memoryCache.jobs) ? [...memoryCache.jobs] : [],
      message: memoryCache.message || '',
      searched: Boolean(memoryCache.searched),
    }
  }

  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return defaults()
    const parsed = JSON.parse(raw)
    const jobs = Array.isArray(parsed.jobs) ? parsed.jobs : []
    const message = typeof parsed.message === 'string' ? parsed.message : ''
    const searched = Boolean(parsed.searched)
    memoryCache = { jobs, message, searched }
    return {
      jobs: [...jobs],
      message,
      searched,
    }
  } catch {
    return defaults()
  }
}

/**
 * @param {{ jobs: unknown[], message?: string }} payload
 */
export function saveCachedSearch({ jobs, message = '' }) {
  const entry = {
    jobs: Array.isArray(jobs) ? jobs : [],
    message,
    searched: true,
  }
  memoryCache = entry
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(entry))
  } catch {
    // Quota or private mode — memory-only cache still works for SPA navigation
  }
}

export function clearCachedSearch() {
  memoryCache = null
  try {
    sessionStorage.removeItem(STORAGE_KEY)
  } catch {
    // ignore
  }
}
