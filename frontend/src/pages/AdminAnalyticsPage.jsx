import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { BarChart2, Activity } from "lucide-react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { useAuth } from "../context/AuthContext";
import { adminAnalyticsApi } from "../api/admin";

export default function AdminAnalyticsPage() {
  const { isAuthenticated, user, token } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated || user?.role !== "manager") {
      navigate("/");
      return;
    }
    let cancelled = false;
    setLoading(true);
    adminAnalyticsApi
      .overview(token)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Failed to load analytics");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, user?.role, token, navigate]);

  const conversionRate =
    data && data.recommendation_conversion_rate != null
      ? (data.recommendation_conversion_rate * 100).toFixed(2)
      : "0.00";

  return (
    <div className="min-h-screen flex flex-col bg-stone-50">
      <Navbar />
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 animate-fade-up">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="font-serif text-2xl font-medium text-gray-900">
                Analytics Overview
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Category performance and recommendation effectiveness.
              </p>
            </div>
          </div>

          {loading ? (
            <p className="text-gray-500 text-sm">Loading analytics...</p>
          ) : error ? (
            <p className="text-red-500 text-sm">{error}</p>
          ) : !data ? (
            <p className="text-gray-500 text-sm">No data.</p>
          ) : (
            <div className="space-y-8">
              <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-white rounded-xl border border-gray-100 p-4">
                  <p className="text-xs uppercase text-gray-400 font-semibold mb-1">
                    Total Orders
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {data.total_orders}
                  </p>
                </div>
                <div className="bg-white rounded-xl border border-gray-100 p-4">
                  <p className="text-xs uppercase text-gray-400 font-semibold mb-1">
                    Total Items Sold
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {data.total_items}
                  </p>
                </div>
                <div className="bg-white rounded-xl border border-gray-100 p-4">
                  <p className="text-xs uppercase text-gray-400 font-semibold mb-1">
                    Recommendation Conversion
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {conversionRate}%
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {data.recommendation_conversions} /{" "}
                    {data.recommendation_impressions} impressions
                  </p>
                </div>
              </section>

              <section className="bg-white rounded-xl border border-gray-100 p-5">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <BarChart2 size={16} className="text-gray-500" />
                    <h2 className="text-sm font-semibold text-gray-900">
                      Category Heatmap (by items sold)
                    </h2>
                  </div>
                </div>
                {Object.keys(data.category_purchase_counts || {}).length === 0 ? (
                  <p className="text-sm text-gray-500">
                    No category data yet. Make some orders first.
                  </p>
                ) : (
                  <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
                    {Object.entries(data.category_purchase_counts).map(
                      ([catId, count]) => (
                        <div
                          key={catId}
                          className="p-3 rounded-lg bg-gray-50 border border-gray-100"
                        >
                          <p className="text-xs text-gray-500 mb-1">
                            Category #{catId}
                          </p>
                          <p className="text-base font-semibold text-gray-900">
                            {count}
                          </p>
                          <p className="text-[10px] text-gray-400">
                            items sold
                          </p>
                        </div>
                      )
                    )}
                  </div>
                )}
              </section>

              <section className="bg-white rounded-xl border border-gray-100 p-5">
                <div className="flex items-center gap-2 mb-3">
                  <Activity size={16} className="text-gray-500" />
                  <h2 className="text-sm font-semibold text-gray-900">
                    Notes
                  </h2>
                </div>
                <ul className="list-disc list-inside text-xs text-gray-500 space-y-1">
                  <li>
                    Conversion được tính gần đúng dựa trên{" "}
                    <code>RecommendationCache</code> và các đơn đã thanh toán.
                  </li>
                  <li>
                    Category ID hiện hiển thị theo ID thô; có thể mở rộng để
                    join sang tên category từ catalog-service nếu cần.
                  </li>
                </ul>
              </section>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}

