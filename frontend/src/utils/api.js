const TOKEN_KEY = 'access_token';

export function authHeaders(extra = {}) {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}`, ...extra } : { ...extra };
}

export async function apiFetch(url, options = {}) {
  const { headers: extraHeaders, ...rest } = options;
  const response = await fetch(url, {
    ...rest,
    headers: authHeaders(extraHeaders),
  });

  // If the token is invalid/expired, automatically log out
  if (response.status === 401 && localStorage.getItem(TOKEN_KEY)) {
    localStorage.removeItem(TOKEN_KEY);
    window.location.href = '/login';
  }

  return response;
}
