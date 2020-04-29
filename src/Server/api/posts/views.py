from rest_framework import generics, permissions, mixins, response, status
from ..core import get_model
from ..dashboard.mixins import ProfileObject
from .serializers import PostCreateSerializer, PostListSerializer, PostRetrieveUpdateSerializer
from ..dashboard.permissions import *
from ..dashboard.pagination import StandardResultPagination
Post = get_model("posts", "Post")
Comment = get_model("comments", "Comment")


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultPagination

    def get_queryset(self):
        return Post.objects.all()


class PostRetrieveUpdateDestroyAPIView(ProfileObject, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostRetrieveUpdateSerializer
    permission_classes = [IsAdmin]
    queryset = Post.objects.all()
    lookup_field = "slug"

    def perform_update(self, serializer):
        serializer.save(author=self.get_user_profile())


class PostCreateAPIView(ProfileObject, generics.CreateAPIView):
    serializer_class = PostCreateSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_context(self):
        ctx = super(PostCreateAPIView, self).get_serializer_context()
        ctx["author"] = self.get_user_profile()
        return ctx


class ToggleLikePost(generics.views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug, *args, **kwargs):
        user = request.user
        post = generics.get_object_or_404(Post.objects.all(), slug=slug)
        liked = Post.objects.toggle_like(user, post)
        return response.Response(liked, status=status.HTTP_200_OK, headers={})
