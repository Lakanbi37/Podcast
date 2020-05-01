from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser
from ..dashboard.permissions import IsCEO
from .serializers import *


class MembershipListCreateAPIView(ListCreateAPIView):
    serializer_class = MembershipModelSerializer
    queryset = Membership.objects.all()
    permission_classes = [IsAdminUser, IsCEO]


class MembershipRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Membership.objects.all()
    serializer_class = MembershipModelSerializer
    permission_classes = [IsAdminUser, IsCEO]
    lookup_field = "slug"