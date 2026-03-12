from django.urls import path
from .views import RatingListView, BookRatingSummaryView, CommentListView, CommentDetailView

urlpatterns = [
    path("ratings/", RatingListView.as_view(), name="rating-list"),
    path("ratings/book/<int:book_id>/summary/", BookRatingSummaryView.as_view(), name="rating-summary"),
    path("comments/", CommentListView.as_view(), name="comment-list"),
    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
]
