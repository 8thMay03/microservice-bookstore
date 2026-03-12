const PLACEHOLDER_IMAGE = "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600&q=80";

/** Map API book to frontend format for BookCard/BookDetailPage */
export function normalizeBook(apiBook) {
  if (!apiBook) return null;
  const created = apiBook.created_at ? new Date(apiBook.created_at) : null;
  const isNew = created && (Date.now() - created) < 90 * 24 * 60 * 60 * 1000; // within 90 days
  return {
    id: apiBook.id,
    title: apiBook.title,
    author: apiBook.author,
    price: Number(apiBook.price),
    image: apiBook.cover_image || PLACEHOLDER_IMAGE,
    isNew,
    rating: apiBook.rating ?? null,
    reviewCount: apiBook.review_count ?? null,
    description: apiBook.description || "",
    pages: apiBook.pages,
    isbn: apiBook.isbn,
    category_id: apiBook.category_id,
    published_date: apiBook.published_date,
    language: apiBook.language,
    inventory: apiBook.inventory,
  };
}
