from django.db.models import Q
from rest_framework import generics, permissions, filters
from .serializers import DiscussionModelSerializer, DiscussionSerializer
from ..core import get_model
# from ..dashboard.permissions import *
from ..dashboard.pagination import StandardResultPagination

Discussion = get_model("forum", "Discussion")


class DiscussionListView(generics.ListAPIView):
    serializer_class = DiscussionSerializer
    pagination_class = StandardResultPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "user__username"]

    def get_queryset(self):
        qs = Discussion.objects.all()
        query = self.request.GET.get("query", "")
        if query != "":
            qs = qs.filter(
                Q(name__icontains=query)
            )
        return qs


class DiscussionCreateAPIView(generics.CreateAPIView):
    serializer_class = DiscussionModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Discussion.objects.all()

    def get_serializer_context(self):
        ctx = super(DiscussionCreateAPIView, self).get_serializer_context()
        ctx["user"] = self.request.user
        return ctx


class DiscussionRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DiscussionModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        return Discussion.objects.all()

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get(self, request, *args, **kwargs):
        _model = self.get_object()
        Discussion.objects.view(_model, request.user)
        return self.retrieve(request, *args, **kwargs)
