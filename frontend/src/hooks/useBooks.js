import { useState, useEffect, useCallback } from "react";
import { booksApi } from "../api/books";
import { normalizeBook } from "../utils/bookUtils";
import { books as fallbackBooks } from "../data/books";

function toDisplayBook(b) {
  return {
    id: b.id,
    title: b.title,
    author: b.author,
    price: Number(b.price),
    image: b.image || b.cover_image,
    isNew: b.isNew ?? true,
    rating: b.rating ?? null,
    reviewCount: b.reviewCount ?? b.review_count ?? null,
    category_id: b.category_id ?? b.category,
    description: b.description || "",
    pages: b.pages,
    isbn: b.isbn,
    published_date: b.published_date || b.year,
    language: b.language,
  };
}

export function useBooks(params = {}) {
  const [data, setData] = useState({ results: [], total: 0, page: 1 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchBooks = useCallback(async (opts = {}) => {
    setLoading(true);
    setError(null);
    try {
      const merged = { ...params, ...opts };
      if (merged.category_id === "all" || merged.category_id == null) delete merged.category_id;
      const res = await booksApi.list(merged);
      setData({
        results: (res.results || []).map(normalizeBook).filter(Boolean),
        total: res.total ?? 0,
        page: res.page ?? 1,
        pageSize: res.page_size ?? 20,
      });
    } catch (err) {
      setError(err.message);
      const merged = { ...params, ...opts };
      const catId = merged?.category_id;
      const filtered = catId && catId !== "all"
        ? fallbackBooks.filter((b) => b.category === catId || b.category_id === catId)
        : fallbackBooks;
      setData({
        results: filtered.map(toDisplayBook),
        total: filtered.length,
        page: 1,
        pageSize: 20,
      });
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(params)]);

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  return { ...data, loading, error, refetch: fetchBooks };
}
