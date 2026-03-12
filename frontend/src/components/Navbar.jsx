import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import {
  Search, ShoppingBag, User, BookMarked,
  X, Menu, LogOut, ChevronDown,
} from "lucide-react";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import CartSidebar from "./CartSidebar";

const NAV_LINKS = [
  { to: "/", label: "Discover" },
  { to: "/category/all", label: "Browse" },
];

export default function Navbar() {
  const { totalItems, setIsOpen: openCart } = useCart();
  const { user, isAuthenticated, logout } = useAuth();

  const [searchOpen, setSearchOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/category/all?search=${encodeURIComponent(query.trim())}`);
      setSearchOpen(false);
      setQuery("");
    }
  };

  const handleLogout = () => {
    logout();
    setUserMenuOpen(false);
    navigate("/");
  };

  return (
    <>
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-gray-100">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16 gap-6">
            {/* Logo */}
            <Link
              to="/"
              className="flex items-center gap-2 text-gray-900 shrink-0"
              aria-label="Bookstore home"
            >
              <BookMarked size={22} strokeWidth={1.8} />
            </Link>

            {/* Desktop nav */}
            <ul className="hidden md:flex items-center gap-1">
              {NAV_LINKS.map(({ to, label }) => (
                <li key={to}>
                  <NavLink
                    to={to}
                    end={to === "/"}
                    className={({ isActive }) =>
                      `px-3 py-1.5 rounded-full text-sm transition-all duration-150 ${
                        isActive
                          ? "bg-gray-900 text-white font-medium"
                          : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                      }`
                    }
                  >
                    {label}
                  </NavLink>
                </li>
              ))}
            </ul>

            <div className="flex-1" />

            {/* Search bar */}
            {searchOpen && (
              <form
                onSubmit={handleSearch}
                className="hidden md:flex items-center bg-gray-100 rounded-full px-4 py-2 w-56 gap-2"
              >
                <Search size={14} className="text-gray-400 shrink-0" />
                <input
                  autoFocus
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search books..."
                  className="bg-transparent text-sm outline-none flex-1 text-gray-900 placeholder-gray-400 w-full"
                />
                <button
                  type="button"
                  onClick={() => { setSearchOpen(false); setQuery(""); }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={14} />
                </button>
              </form>
            )}

            {/* Icon actions */}
            <div className="flex items-center gap-1">
              {!searchOpen && (
                <button
                  onClick={() => setSearchOpen(true)}
                  className="p-2 rounded-full text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
                  aria-label="Search"
                >
                  <Search size={18} />
                </button>
              )}

              {/* Cart */}
              <button
                onClick={() => openCart(true)}
                className="relative p-2 rounded-full text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
                aria-label={`Cart (${totalItems} items)`}
              >
                <ShoppingBag size={18} />
                {totalItems > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-[#e8392a] text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                    {totalItems > 9 ? "9+" : totalItems}
                  </span>
                )}
              </button>

              {/* Auth section */}
              {isAuthenticated ? (
                /* User avatar + dropdown */
                <div className="relative hidden sm:block">
                  <button
                    onClick={() => setUserMenuOpen((v) => !v)}
                    className="flex items-center gap-2 ml-1 pl-2 pr-3 py-1.5 rounded-full hover:bg-gray-100 transition-colors"
                  >
                    <div className="w-7 h-7 rounded-full bg-gray-900 text-white text-xs font-semibold flex items-center justify-center shrink-0">
                      {user?.first_name?.charAt(0).toUpperCase() ?? <User size={14} />}
                    </div>
                    <span className="text-sm font-medium text-gray-700 max-w-[90px] truncate">
                      {user?.first_name ?? "Account"}
                    </span>
                    <ChevronDown
                      size={13}
                      className={`text-gray-400 transition-transform ${userMenuOpen ? "rotate-180" : ""}`}
                    />
                  </button>

                  {userMenuOpen && (
                    <>
                      <div className="fixed inset-0 z-10" onClick={() => setUserMenuOpen(false)} />
                      <div className="absolute right-0 top-full mt-2 z-20 bg-white border border-gray-200 rounded-xl shadow-lg py-1.5 min-w-[180px]">
                        <div className="px-4 py-2.5 border-b border-gray-100">
                          <p className="text-sm font-medium text-gray-900">
                            {user?.first_name} {user?.last_name}
                          </p>
                          <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                        </div>
                        {(user?.role === "manager" || user?.role === "staff") && (
                          <Link
                            to="/admin/books"
                            onClick={() => setUserMenuOpen(false)}
                            className="flex items-center gap-2.5 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                          >
                            Manage Books
                          </Link>
                        )}
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                        >
                          <LogOut size={14} />
                          Sign out
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                /* Log In / Register buttons */
                <div className="hidden sm:flex items-center gap-2 ml-1">
                  <Link
                    to="/login"
                    className="text-sm font-medium text-gray-600 hover:text-gray-900 px-3 py-1.5 rounded-full hover:bg-gray-100 transition-colors"
                  >
                    Log in
                  </Link>
                  <Link
                    to="/register"
                    className="btn-primary text-sm px-4 py-2"
                  >
                    Sign up
                  </Link>
                </div>
              )}

              {/* Mobile hamburger */}
              <button
                className="flex md:hidden p-2 text-gray-600 hover:text-gray-900"
                onClick={() => setMobileMenuOpen((v) => !v)}
                aria-label="Menu"
              >
                {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
              </button>
            </div>
          </div>

          {/* Mobile menu */}
          {mobileMenuOpen && (
            <div className="md:hidden border-t border-gray-100 py-3 space-y-0.5">
              {NAV_LINKS.map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === "/"}
                  onClick={() => setMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    `block px-4 py-2.5 text-sm rounded-lg mx-1 ${
                      isActive
                        ? "bg-gray-900 text-white font-medium"
                        : "text-gray-600 hover:bg-gray-100"
                    }`
                  }
                >
                  {label}
                </NavLink>
              ))}

              <div className="pt-2 mt-2 border-t border-gray-100 mx-1">
                {isAuthenticated ? (
                  <>
                    {(user?.role === "manager" || user?.role === "staff") && (
                      <Link
                        to="/admin/books"
                        onClick={() => setMobileMenuOpen(false)}
                        className="block px-4 py-2.5 text-sm text-gray-700 rounded-lg hover:bg-gray-100"
                      >
                        Manage Books
                      </Link>
                    )}
                    <button
                      onClick={() => { handleLogout(); setMobileMenuOpen(false); }}
                      className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                    >
                      <LogOut size={14} /> Sign out ({user?.first_name})
                    </button>
                  </>
                ) : (
                  <div className="flex gap-2 px-1 pt-1">
                    <Link
                      to="/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex-1 text-center py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                      Log in
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex-1 text-center py-2.5 bg-gray-900 rounded-lg text-sm font-medium text-white hover:bg-gray-700"
                    >
                      Sign up
                    </Link>
                  </div>
                )}
              </div>
            </div>
          )}
        </nav>
      </header>

      <CartSidebar />
    </>
  );
}
