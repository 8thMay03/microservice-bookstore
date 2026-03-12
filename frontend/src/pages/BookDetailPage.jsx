import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import {
  ShoppingBag,
  Heart,
  ArrowLeft,
  BookOpen,
  Building2,
  Calendar,
  Hash,
  Share2,
  ChevronRight,
  Check,
} from "lucide-react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import BookCard from "../components/BookCard";
import StarRating from "../components/StarRating";
import { getBookById, getRelatedBooks, categories } from "../data/books";
import { useCart } from "../context/CartContext";

const SAMPLE_REVIEWS = [
  {
    id: 1,
    author: "James M.",
    rating: 5,
    date: "February 2024",
    text: "An absolutely essential addition to any design library. The production quality is superb and the curation of work is thoughtful and comprehensive.",
  },
  {
    id: 2,
    author: "Clara T.",
    rating: 4,
    date: "January 2024",
    text: "Beautiful book. Some of the earlier work could have been given more space, but overall a worthy survey of a remarkable body of work.",
  },
];

export default function BookDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const book = getBookById(id);
  const { addToCart } = useCart();
  const [added, setAdded] = useState(false);
  const [wishlisted, setWishlisted] = useState(false);

  if (!book) {
    return (
      <div className="min-h-screen flex flex-col bg-stone-50">
        <Navbar />
        <div className="flex-1 flex flex-col items-center justify-center gap-4 text-center px-4">
          <BookOpen size={40} className="text-gray-300" />
          <h1 className="font-serif text-2xl font-medium text-gray-900">
            Book not found
          </h1>
          <p className="text-gray-500">
            This book doesn't exist or may have been removed.
          </p>
          <Link to="/category/all" className="btn-primary mt-2">
            Browse all books
          </Link>
        </div>
        <Footer />
      </div>
    );
  }

  const relatedBooks = getRelatedBooks(book);
  const categoryLabel = categories.find((c) => c.id === book.category)?.label ?? book.category;

  const handleAddToCart = () => {
    addToCart(book);
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  };

  return (
    <div className="min-h-screen flex flex-col bg-stone-50">
      <Navbar />

      <main className="flex-1">
        {/* ── Breadcrumb ──────────────────────────────────────────── */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-2">
          <nav className="flex items-center gap-1.5 text-xs text-gray-400">
            <Link to="/" className="hover:text-gray-600 transition-colors">
              Home
            </Link>
            <ChevronRight size={12} />
            <Link
              to={`/category/${book.category}`}
              className="hover:text-gray-600 transition-colors"
            >
              {categoryLabel}
            </Link>
            <ChevronRight size={12} />
            <span className="text-gray-600 truncate max-w-[200px]">{book.title}</span>
          </nav>
        </div>

        {/* ── Main detail layout ──────────────────────────────────── */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16">
            {/* Left: cover ──────────────────────────────────────── */}
            <div className="lg:col-span-5 xl:col-span-4">
              <div className="sticky top-24">
                {/* Main image */}
                <div className="relative bg-white rounded-2xl overflow-hidden shadow-sm">
                  {book.isNew && (
                    <span className="absolute top-4 left-4 z-10 bg-[#e8392a] text-white text-xs font-semibold px-3 py-1.5 rounded-full">
                      New
                    </span>
                  )}
                  <img
                    src={book.image}
                    alt={book.title}
                    className="w-full aspect-[4/5] object-cover"
                  />
                </div>

                {/* Thumbnail strip (uses same image for demo) */}
                <div className="flex gap-2 mt-3">
                  {[book.image, book.image, book.image].map((src, i) => (
                    <button
                      key={i}
                      className={`w-16 h-20 rounded-lg overflow-hidden border-2 transition-colors ${
                        i === 0 ? "border-gray-900" : "border-transparent hover:border-gray-300"
                      }`}
                    >
                      <img
                        src={src}
                        alt=""
                        className="w-full h-full object-cover opacity-80"
                      />
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Right: info ───────────────────────────────────────── */}
            <div className="lg:col-span-7 xl:col-span-8 space-y-6">
              {/* Category tag */}
              <Link
                to={`/category/${book.category}`}
                className="inline-block text-xs font-semibold tracking-widest uppercase text-gray-400 hover:text-gray-700 transition-colors"
              >
                {categoryLabel}
              </Link>

              {/* Title & author */}
              <div>
                <h1 className="font-serif text-3xl sm:text-4xl font-medium text-gray-900 leading-tight">
                  {book.title}
                </h1>
                <p className="text-gray-600 mt-2 text-lg">by {book.author}</p>
              </div>

              {/* Rating */}
              <StarRating
                rating={book.rating}
                reviewCount={book.reviewCount}
                size="md"
              />

              {/* Price */}
              <div className="flex items-baseline gap-3 pt-1">
                <span className="font-serif text-4xl font-semibold text-gray-900">
                  ${book.price}
                </span>
                <span className="text-sm text-gray-400">Free shipping over $50</span>
              </div>

              {/* Tags */}
              {book.tags && (
                <div className="flex flex-wrap gap-2">
                  {book.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-600"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              <hr className="border-gray-100" />

              {/* CTA buttons */}
              <div className="flex gap-3">
                <button
                  onClick={handleAddToCart}
                  className={`flex-1 flex items-center justify-center gap-2.5 py-3.5 rounded-full font-medium text-sm transition-all duration-200 ${
                    added
                      ? "bg-green-600 text-white"
                      : "bg-gray-900 text-white hover:bg-gray-700"
                  }`}
                >
                  {added ? (
                    <>
                      <Check size={16} /> Added to cart!
                    </>
                  ) : (
                    <>
                      <ShoppingBag size={16} /> Add to Cart — ${book.price}
                    </>
                  )}
                </button>

                <button
                  onClick={() => setWishlisted((v) => !v)}
                  className={`w-12 h-12 rounded-full border flex items-center justify-center transition-all duration-150 shrink-0 ${
                    wishlisted
                      ? "bg-red-50 border-red-200 text-red-500"
                      : "border-gray-200 text-gray-500 hover:border-gray-400 hover:text-gray-700"
                  }`}
                  aria-label={wishlisted ? "Remove from wishlist" : "Add to wishlist"}
                >
                  <Heart size={17} fill={wishlisted ? "currentColor" : "none"} />
                </button>

                <button
                  className="w-12 h-12 rounded-full border border-gray-200 flex items-center justify-center text-gray-500 hover:border-gray-400 hover:text-gray-700 transition-colors shrink-0"
                  aria-label="Share"
                >
                  <Share2 size={17} />
                </button>
              </div>

              <hr className="border-gray-100" />

              {/* Description */}
              <div>
                <h2 className="font-serif text-lg font-semibold mb-3 text-gray-900">
                  About this book
                </h2>
                <p className="text-gray-600 leading-relaxed text-sm">{book.description}</p>
              </div>

              {/* Specs */}
              <div className="bg-white rounded-2xl border border-gray-100 p-5">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">
                  Book Details
                </h3>
                <dl className="grid grid-cols-2 gap-x-6 gap-y-3">
                  {[
                    { icon: BookOpen, label: "Pages", value: book.pages },
                    { icon: Building2, label: "Publisher", value: book.publisher },
                    { icon: Calendar, label: "Year", value: book.year },
                    { icon: Hash, label: "ISBN", value: book.isbn },
                  ].map(({ icon: Icon, label, value }) => (
                    <div key={label} className="flex items-start gap-2.5">
                      <Icon size={14} className="text-gray-400 mt-0.5 shrink-0" />
                      <div>
                        <dt className="text-xs text-gray-400">{label}</dt>
                        <dd className="text-sm font-medium text-gray-700 mt-0.5">
                          {value}
                        </dd>
                      </div>
                    </div>
                  ))}
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* ── Customer Reviews ───────────────────────────────────── */}
        <section className="border-t border-gray-200 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
            <div className="max-w-3xl">
              <div className="flex items-center justify-between mb-8">
                <h2 className="font-serif text-2xl font-medium">
                  Customer Reviews
                </h2>
                <div className="flex flex-col items-end gap-1">
                  <StarRating
                    rating={book.rating}
                    reviewCount={book.reviewCount}
                    size="lg"
                  />
                </div>
              </div>

              <div className="space-y-6">
                {SAMPLE_REVIEWS.map((review) => (
                  <div
                    key={review.id}
                    className="border-b border-gray-100 pb-6 last:border-0"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-gray-900 text-white text-xs font-semibold flex items-center justify-center">
                          {review.author.charAt(0)}
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {review.author}
                        </span>
                      </div>
                      <span className="text-xs text-gray-400">{review.date}</span>
                    </div>
                    <StarRating
                      rating={review.rating}
                      showCount={false}
                      size="xs"
                    />
                    <p className="mt-2 text-sm text-gray-600 leading-relaxed">
                      {review.text}
                    </p>
                  </div>
                ))}
              </div>

              <button className="mt-6 btn-outline">
                View all {book.reviewCount} reviews
              </button>
            </div>
          </div>
        </section>

        {/* ── Related Books ──────────────────────────────────────── */}
        {relatedBooks.length > 0 && (
          <section className="border-t border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
              <div className="flex items-center justify-between mb-8">
                <h2 className="font-serif text-2xl font-medium">
                  You might also like
                </h2>
                <Link
                  to={`/category/${book.category}`}
                  className="text-sm text-gray-500 hover:text-gray-900 flex items-center gap-1 transition-colors"
                >
                  More in {categoryLabel}
                  <ChevronRight size={14} />
                </Link>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-5 gap-y-10">
                {relatedBooks.map((b) => (
                  <BookCard key={b.id} book={b} showRating />
                ))}
              </div>
            </div>
          </section>
        )}
      </main>

      <Footer />
    </div>
  );
}
