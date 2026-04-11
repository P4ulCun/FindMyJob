const TOKEN_KEY = 'access_token';

export function authHeaders(extra = {}) {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}`, ...extra } : { ...extra };
}

export async function apiFetch(url, options = {}) {
  const { headers: extraHeaders, ...rest } = options;
  return fetch(url, {
    ...rest,
    headers: authHeaders(extraHeaders),
  });
}
