import { Link } from "react-router-dom";
import { ArrowUpRight, ShoppingBag } from "lucide-react";
import StarRating from "./StarRating";
import { useCart } from "../context/CartContext";

export default function BookCard({ book, showRating = false }) {
  const { addToCart } = useCart();
  if (!book) return null;

  return (
    <article className="book-card group cursor-pointer">
      {/* Image container */}
      <Link to={`/book/${book.id}`} className="block relative overflow-hidden bg-gray-50 rounded-sm">
        {/* Badges */}
        {book.isNew && (
          <span className="absolute top-3 left-3 z-10 bg-[#e8392a] text-white text-xs font-semibold px-2.5 py-1 rounded-full tracking-wide">
            New
          </span>
        )}

        {/* Arrow link */}
        <span className="absolute top-3 right-3 z-10 w-7 h-7 bg-gray-900/80 backdrop-blur-sm rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-all duration-200 translate-x-1 group-hover:translate-x-0">
          <ArrowUpRight size={13} />
        </span>

        {/* Book cover */}
        <div className="aspect-[3/4] overflow-hidden">
          <img
            src={book.image}
            alt={book.title}
            className="book-card-img w-full h-full object-cover"
            loading="lazy"
            decoding="async"
          />
        </div>
      </Link>

      {/* Info row */}
      <div className="mt-3 px-0.5">
        <div className="flex items-start justify-between gap-2">
          <Link to={`/book/${book.id}`} className="flex-1 min-w-0">
            <h3 className="text-sm font-medium text-gray-900 leading-snug line-clamp-2 hover:text-gray-600 transition-colors">
              {book.title}
            </h3>
            <p className="text-xs text-gray-500 mt-0.5 truncate">{book.author}</p>
          </Link>
          <p className="text-sm font-semibold text-gray-900 shrink-0">${Number(book.price || 0).toFixed(2)}</p>
        </div>

        {showRating && (
          <div className="mt-2">
            <StarRating rating={book.rating} reviewCount={book.reviewCount} size="xs" />
          </div>
        )}

        {/* Quick add button */}
        <button
          onClick={() => addToCart(book)}
          className="mt-3 w-full flex items-center justify-center gap-2 py-2 border border-gray-200 rounded-full text-xs font-medium text-gray-700 hover:bg-gray-900 hover:text-white hover:border-gray-900 transition-all duration-150 opacity-0 group-hover:opacity-100"
        >
          <ShoppingBag size={12} />
          Add to cart
        </button>
      </div>
    </article>
  );
}
