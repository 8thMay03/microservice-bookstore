import { Link, useParams, useSearchParams } from "react-router-dom";
import {
  Sparkles,
  LayoutGrid,
  Building2,
  PenLine,
  Atom,
  Camera,
} from "lucide-react";
import { categories } from "../data/books";

const ICON_MAP = {
  sparkles: Sparkles,
  "layout-grid": LayoutGrid,
  "building-2": Building2,
  "pen-line": PenLine,
  atom: Atom,
  camera: Camera,
};

export default function CategoryFilter({ activeCategory = "all", onSelect }) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide py-1">
      {categories.map((cat) => {
        const Icon = cat.icon ? ICON_MAP[cat.icon] : null;
        const isActive = cat.id === activeCategory;

        const content = (
          <>
            {Icon && <Icon size={13} className="shrink-0" />}
            <span>{cat.label}</span>
          </>
        );

        if (onSelect) {
          return (
            <button
              key={cat.id}
              onClick={() => onSelect(cat.id)}
              className={`pill whitespace-nowrap ${isActive ? "pill-active" : "pill-inactive"}`}
            >
              {content}
            </button>
          );
        }

        return (
          <Link
            key={cat.id}
            to={`/category/${cat.id}`}
            className={`pill whitespace-nowrap ${isActive ? "pill-active" : "pill-inactive"}`}
          >
            {content}
          </Link>
        );
      })}

      <Link
        to="/category/all"
        className="pill whitespace-nowrap pill-inactive ml-auto"
      >
        See More
      </Link>
    </div>
  );
}
