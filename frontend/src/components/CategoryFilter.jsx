import { Link } from "react-router-dom";

const DEFAULT_CATEGORIES = [
  { id: "all", name: "All" },
];

export default function CategoryFilter({ activeCategory = "all", onSelect, categories = DEFAULT_CATEGORIES }) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide py-1">
      {categories.map((cat) => {
        const Icon = null;
        const isActive = String(cat.id) === String(activeCategory);

        const content = (
          <>
            {Icon && <Icon size={13} className="shrink-0" />}
            <span>{cat.name}</span>
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
