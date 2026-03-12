import { Star } from "lucide-react";

export default function StarRating({ rating, reviewCount, size = "sm", showCount = true }) {
  const sizeMap = {
    xs: { star: 10, text: "text-xs" },
    sm: { star: 13, text: "text-sm" },
    md: { star: 16, text: "text-sm" },
    lg: { star: 20, text: "text-base" },
  };
  const { star, text } = sizeMap[size] ?? sizeMap.sm;

  return (
    <div className={`flex items-center gap-1.5 ${text}`}>
      <div className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map((n) => {
          const filled = n <= Math.floor(rating);
          const half = !filled && n - 0.5 <= rating;
          return (
            <span key={n} className="relative inline-flex">
              {/* Empty star base */}
              <Star size={star} className="text-gray-200 fill-gray-200" />
              {/* Filled overlay */}
              {(filled || half) && (
                <span
                  className="absolute inset-0 overflow-hidden"
                  style={{ width: filled ? "100%" : "50%" }}
                >
                  <Star size={star} className="text-amber-400 fill-amber-400" />
                </span>
              )}
            </span>
          );
        })}
      </div>
      {showCount && reviewCount !== undefined && (
        <span className="text-gray-500">
          {rating.toFixed(1)}
          <span className="ml-1 text-gray-400">({reviewCount})</span>
        </span>
      )}
    </div>
  );
}
