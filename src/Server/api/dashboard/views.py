from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, response, status, filters
from .utils import RoleAssignor
from .pagination import StandardResultPagination
from .permissions import *
from .serializers import *

User = get_user_model()
BAD_REQ = status.HTTP_400_BAD_REQUEST
REQ_OK = status.HTTP_200_OK
REQ_NOT_FOUND = status.HTTP_404_NOT_FOUND

queryset = Profile.objects.all()


class AuthorListAPIView(generics.ListAPIView):
    serializer_class = ProfileListSerializer
    permission_classes = [IsCEO]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    pagination_class = StandardResultPagination
    search_fields = ["name", "street", "zip_code", "city", "user__username", "phone"]

    def get_queryset(self):
        qs = queryset
        query = self.request.GET.get("query", "")
        if query != "":
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(street__icontains=query) |
                Q(city__icontains=query) |
                Q(user__username__icontains=query) |
                Q(zip_code__icontains=query) |
                Q(phone__icontains=query)
            )
        return qs


class AssignUserRole(RoleAssignor, generics.views.APIView):
    permission_classes = [IsCEO]

    def post(self, request, **kwargs):
        ser = PermissionSerializer(data=request.data)
        user = self.get_user(self.kwargs.get("user_id"))
        try:
            if ser.is_valid(raise_exception=True):
                perm = self.get_permission(ser.validated_data["role"], kwargs["user_id"])
                self.assign_role(perm, user, ser.validated_data["role"])
                return response.Response(ser.data, status=REQ_OK, headers={})
            return response.Response(ser.errors, status=BAD_REQ, headers={})
        except Exception as e:
            print(str(e))
            return response.Response({"error": f"{str(e)}"}, status=BAD_REQ)
