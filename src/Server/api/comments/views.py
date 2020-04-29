from django.db.models import Q
from rest_framework import generics, permissions, filters
from .serializers import *
from ..core import get_model
from ..dashboard.permissions import IsOwnerOrReadOnly
from ..dashboard.pagination import StandardResultPagination

Post = get_model("posts", "Post")
Comment = get_model("comments", "Comment")


class CommentCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        model_type = self.request.GET.get("model_type")
        app_label = self.request.GET.get("app_label")
        slug = self.request.GET.get("slug")
        parent_id = self.request.GET.get("parent_id", None)
        return comment_create_func(
            app_name=app_label, model_type=model_type, slug=slug,
            parent_id=parent_id, user=self.request.user
        )


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentDetailSerializer
    queryset = Comment.objects.filter(id__gte=0)
    permission_classes = [IsOwnerOrReadOnly]


class PostCommentListAPIView(generics.ListAPIView):
    serializer_class = CommentDetailSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["content", "user__username", "user__first_name", "user__last_name"]

    def get_object(self):
        obj = generics.get_object_or_404(Post.objects.all(), id=self.kwargs.get("post_id"))
        return obj

    def get_queryset(self):
        qs = self.get_object().comments
        query = self.request.GET.get("q", "")
        if query != "":
            qs = qs.filter(Q(content__icontains=query) |
                           Q(user__username__icontains=query)
                           )
        return qs
