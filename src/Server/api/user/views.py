from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, filters
from .serializers import UserDiscussionSerializer, UserModelSerializer
from ..core import get_model

Discussion = get_model("forum", "Discussion")

User = get_user_model()


class UserAPIView(generics.RetrieveAPIView):
    serializer_class = UserModelSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return self.request.user


class UserDetailsAPIView(generics.RetrieveAPIView):
    serializer_class = UserModelSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    lookup_field = "username"


class UserDiscussionAPIView(generics.ListAPIView):
    serializer_class = UserDiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    model = Discussion

    def get_queryset(self):
        qs = self.model.objects.filter(user=self.request.user)
        return qs
