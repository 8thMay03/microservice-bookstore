async function request(url, options = {}, token = null) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const detail = data.detail || data.error || `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}

export const catalogApi = {
  listCategories: (token = null) =>
    request("/api/catalog/categories/", {}, token),
};
