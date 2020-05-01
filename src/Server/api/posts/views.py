from django.db.models import Q
from django.http import Http404
from rest_framework import generics, permissions, exceptions, response, status
from ..dashboard.mixins import ProfileObject
from .serializers import *
from ..dashboard.permissions import *
from ..dashboard.pagination import StandardResultPagination
from ..membership.mixins import IsSufficientMembership, IsCategoryMembership


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultPagination

    def get_queryset(self):
        return Post.objects.all()


class PostRetrieveUpdateDestroyAPIView(ProfileObject, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostRetrieveUpdateSerializer
    permission_classes = [IsSufficientMembership, IsAdmin]
    queryset = Post.objects.all()
    lookup_field = "slug"

    def perform_update(self, serializer):
        serializer.save(author=self.get_user_profile())

    def get_serializer_context(self):
        ctx = super(PostRetrieveUpdateDestroyAPIView, self).get_serializer_context()
        ctx["request"] = self.request
        return ctx


class PostCreateAPIView(ProfileObject, generics.CreateAPIView):
    serializer_class = PostCreateSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_context(self):
        ctx = super(PostCreateAPIView, self).get_serializer_context()
        ctx["author"] = self.get_user_profile()
        return ctx


class ReactToPostAPIView(generics.CreateAPIView):
    serializer_class = PostLikeModelSerializer
    queryset = PostLike.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_post(self):
        post = generics.get_object_or_404(Post.objects.all(), slug=self.kwargs.get("slug"))
        return post

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, post=self.get_post())


class CategoryRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategoryModelSerializer
    queryset = Category.objects.all()
    permission_classes = [IsSufficientMembership, IsCEO]
    lookup_field = "slug"

    def get_serializer_context(self):
        ctx = super(CategoryRetrieveAPIView, self).get_serializer_context()
        ctx['request'] = self.request
        return ctx


class CategoryListAPIView(generics.ListCreateAPIView):
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()
    permission_classes = [IsCEO]


class PollChoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = PollChoiceModelSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = PollChoice.objects.filter_by_post(self.kwargs.get("post_id"))
        data = self.request.query_params.get
        if data("choice"):
            qs = qs.filter(Q(choice__icontains=data("choice")))
        if data("created"):
            qs = qs.filter(Q(timestamp__date=datetime.date(data("created"))))
        return qs

    def get_post(self,):
        return generics.get_object_or_404(Post.objects.all(), id=self.kwargs.get("post_id"))

    def perform_create(self, serializer):
        serializer.save(post_id=self.kwargs.get("post_id"))

    def get(self, request, *args, **kwargs):
        post = self.get_post()
        if not post.post_type == "poll":
            raise exceptions.ParseError(detail="Post is not a poll")
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.get_post().post_type == "poll":
            raise exceptions.PermissionDenied(detail="You cant create choices for posts that are not polls")
        return self.create(request, *args, **kwargs)


class PollVotesAPIView(generics.views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PollVoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        poll_id = serializer.validated_data.get("poll_id")
        is_voted = PollChoice.objects.vote(poll_id=poll_id, user=request.user)
        _response = {
            "is_voted": is_voted,
            "data": serializer.data
        }
        return response.Response(_response, status=status.HTTP_200_OK)