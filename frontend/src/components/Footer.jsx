import { Link } from "react-router-dom";
import { BookMarked, Instagram, Twitter } from "lucide-react";

const FOOTER_LINKS = {
  Shop: [
    { label: "New Arrivals", to: "/category/all" },
    { label: "Graphic Design", to: "/category/graphic-design" },
    { label: "Architecture", to: "/category/architecture" },
    { label: "Photography", to: "/category/photography" },
    { label: "Fine Arts", to: "/category/fine-arts" },
  ],
  Company: [
    { label: "About Us", to: "/" },
    { label: "Blog", to: "/" },
    { label: "Press", to: "/" },
    { label: "Careers", to: "/" },
  ],
  Support: [
    { label: "FAQ", to: "/" },
    { label: "Shipping", to: "/" },
    { label: "Returns", to: "/" },
    { label: "Contact", to: "/" },
  ],
};

export default function Footer() {
  return (
    <footer className="bg-gray-950 text-gray-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-10">
          {/* Brand */}
          <div className="md:col-span-2">
            <Link to="/" className="flex items-center gap-2 text-white mb-4">
              <BookMarked size={22} strokeWidth={1.8} />
              <span className="font-serif text-lg">Bookstore</span>
            </Link>
            <p className="text-sm text-gray-500 leading-relaxed max-w-xs">
              Explorations into books, reading culture, and the art of
              thoughtful curation. Every book in our collection is chosen with
              care.
            </p>
            <div className="flex gap-3 mt-6">
              <a
                href="#"
                className="w-9 h-9 rounded-full border border-gray-800 flex items-center justify-center text-gray-500 hover:text-white hover:border-gray-600 transition-colors"
                aria-label="Instagram"
              >
                <Instagram size={15} />
              </a>
              <a
                href="#"
                className="w-9 h-9 rounded-full border border-gray-800 flex items-center justify-center text-gray-500 hover:text-white hover:border-gray-600 transition-colors"
                aria-label="Twitter"
              >
                <Twitter size={15} />
              </a>
            </div>
          </div>

          {/* Links */}
          {Object.entries(FOOTER_LINKS).map(([heading, links]) => (
            <div key={heading}>
              <h3 className="text-white text-sm font-semibold mb-4">{heading}</h3>
              <ul className="space-y-2.5">
                {links.map(({ label, to }) => (
                  <li key={label}>
                    <Link
                      to={to}
                      className="text-sm text-gray-500 hover:text-gray-200 transition-colors"
                    >
                      {label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-8 border-t border-gray-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-gray-600">
          <p>© {new Date().getFullYear()} Bookstore. All rights reserved.</p>
          <div className="flex gap-4">
            <a href="#" className="hover:text-gray-400 transition-colors">Privacy</a>
            <a href="#" className="hover:text-gray-400 transition-colors">Terms</a>
            <a href="#" className="hover:text-gray-400 transition-colors">Cookies</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
