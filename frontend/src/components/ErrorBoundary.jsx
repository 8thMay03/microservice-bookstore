import { Component } from "react";
import { Link } from "react-router-dom";
import { AlertCircle } from "lucide-react";

export class ErrorBoundary extends Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("App error:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-stone-50 px-4">
          <AlertCircle size={48} className="text-amber-500 mb-4" />
          <h1 className="font-serif text-2xl font-medium text-gray-900 mb-2">
            Đã xảy ra lỗi
          </h1>
          <p className="text-gray-600 text-sm text-center max-w-md mb-6">
            {this.state.error?.message || "Vui lòng tải lại trang hoặc kiểm tra console để biết chi tiết."}
          </p>
          <Link to="/" className="btn-primary">
            Về trang chủ
          </Link>
        </div>
      );
    }
    return this.props.children;
  }
}
