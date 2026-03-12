from django.db.models import Avg, Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Rating, Comment
from .serializers import RatingSerializer, CommentSerializer, BookRatingSummarySerializer


class RatingListView(APIView):
    """
    GET  /api/reviews/ratings/?book_id=<id>   — ratings for a book
    POST /api/reviews/ratings/                — submit/update a rating
    """

    def get(self, request):
        book_id = request.query_params.get("book_id")
        customer_id = request.query_params.get("customer_id")
        qs = Rating.objects.all()
        if book_id:
            qs = qs.filter(book_id=book_id)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        return Response(RatingSerializer(qs, many=True).data)

    def post(self, request):
        serializer = RatingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        rating, created = Rating.objects.update_or_create(
            book_id=serializer.validated_data["book_id"],
            customer_id=serializer.validated_data["customer_id"],
            defaults={"score": serializer.validated_data["score"]},
        )
        return Response(
            RatingSerializer(rating).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class BookRatingSummaryView(APIView):
    """GET /api/reviews/ratings/book/<book_id>/summary/"""

    def get(self, request, book_id):
        agg = Rating.objects.filter(book_id=book_id).aggregate(
            average_score=Avg("score"), total_ratings=Count("id")
        )
        return Response({
            "book_id": book_id,
            "average_score": round(agg["average_score"] or 0, 2),
            "total_ratings": agg["total_ratings"],
        })


class CommentListView(APIView):
    """
    GET  /api/reviews/comments/?book_id=<id>   — comments for a book
    POST /api/reviews/comments/                — post a comment
    """

    def get(self, request):
        book_id = request.query_params.get("book_id")
        qs = Comment.objects.filter(is_approved=True)
        if book_id:
            qs = qs.filter(book_id=book_id)
        return Response(CommentSerializer(qs, many=True).data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save()
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    """DELETE /api/reviews/comments/<id>/"""

    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
