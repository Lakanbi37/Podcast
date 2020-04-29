from rest_framework import generics, permissions, mixins, response, status

from ..models import Post
import authors.mixins as mxn

from .serializers import PostCreateSerializer, PostListSerializer, PostRetrieveUpdateSerializer


class PostListAPIView(mxn.AuthorObject, mixins.CreateModelMixin, generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Post.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = PostCreateSerializer(data=request.data, context={"author": self.get_request_author()})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class PostRetrieveUpdateDestroyAPIView(mxn.AuthorObject, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostRetrieveUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Post.objects.all()
    lookup_field = "pk"

    def perform_update(self, serializer):
        serializer.save(author=self.get_request_author)


class PostCreateAPIView(mxn.AuthorObject, generics.CreateAPIView):
    serializer_class = PostCreateSerializer
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_context(self):
        ctx = super(PostCreateAPIView, self).get_serializer_context()
        ctx["author"] = self.get_request_author()
        return ctx
