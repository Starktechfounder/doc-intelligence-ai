const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(endpoint: string, options: RequestInit = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed: ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  getHealth: () => request('/health'),
  listDocuments: () => request('/documents'),
  ingestFile: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetch(`${API_BASE_URL}/ingest/file`, {
      method: 'POST',
      body: formData,
    }).then(async (res) => {
      if (!res.ok) throw new Error('Failed to ingest file');
      return res.json();
    });
  },
  query: (query: string, top_k = 3, min_score = 0.0) =>
    request('/query', {
      method: 'POST',
      body: JSON.stringify({ query, top_k, min_score }),
    }),
};
