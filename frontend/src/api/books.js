async function request(url, options = {}, token = null) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url, { ...options, headers });
  const data = res.status === 204 ? {} : await res.json().catch(() => ({}));

  if (!res.ok) {
    const detail =
      data.detail ||
      data.error ||
      data.non_field_errors?.[0] ||
      Object.entries(data)
        .map(([k, v]) => `${k}: ${Array.isArray(v) ? v[0] : v}`)
        .join(" · ") ||
      `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}

export const booksApi = {
  list: (params = {}, token = null) => {
    const q = new URLSearchParams(params).toString();
    return request(`/api/books/${q ? `?${q}` : ""}`, {}, token);
  },

  get: (id, token = null) =>
    request(`/api/books/${id}/`, {}, token),

  create: (data, token) =>
    request("/api/books/", {
      method: "POST",
      body: JSON.stringify(data),
    }, token),

  update: (id, data, token) =>
    request(`/api/books/${id}/`, {
      method: "PUT",
      body: JSON.stringify(data),
    }, token),

  delete: (id, token) =>
    request(`/api/books/${id}/`, { method: "DELETE" }, token),
};
