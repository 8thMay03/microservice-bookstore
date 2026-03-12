import { useState, useEffect, useCallback } from "react";
import { catalogApi } from "../api/catalog";
import { categories as fallbackCategories } from "../data/books";

function flattenCategories(arr) {
  return arr.flatMap((c) => [c, ...(c.children?.length ? flattenCategories(c.children) : [])]);
}

const FALLBACK = [
  { id: "all", name: "All", slug: "all" },
  ...fallbackCategories.slice(1).map((c) => ({ id: c.id, name: c.label || c.name, slug: c.id })),
];

export function useCatalog() {
  const [categories, setCategories] = useState([{ id: "all", name: "All", slug: "all" }]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCategories = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const raw = await catalogApi.listCategories();
      const arr = Array.isArray(raw) ? raw : [];
      const flat = flattenCategories(arr);
      setCategories([{ id: "all", name: "All", slug: "all" }, ...flat]);
    } catch (err) {
      setError(err.message);
      setCategories(FALLBACK);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  return { categories, loading, error, refetch: fetchCategories };
}
