from rest_framework import generics, status, response, permissions
from ..dashboard.permissions import *
from .serializers import *
from ..core import get_model
from ..dashboard.mixins import ProfileObject

Profile = get_model("profiles", "Profile")
SocialLinks = get_model("profiles", "SocialLink")

queryset = Profile.objects.all()
link_qs = SocialLinks.objects.all()


class ProfileListAPIView(generics.ListAPIView):
    serializer_class = ProfileModelSerializer
    queryset = queryset
    permission_classes = [permissions.IsAuthenticated]


class SocialLinkCreateAPIView(ProfileObject, generics.CreateAPIView):
    serializer_class = SocialLinkSerializer
    queryset = link_qs
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(profile=self.get_user_profile)


class SocialLinkRetrieveUpdateDeleteAPIView(ProfileObject, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SocialLinkSerializer
    queryset = link_qs
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "username"

    def get_object(self):
        return generics.get_object_or_404(link_qs, user__username=self.kwargs.get("username"))

    def perform_update(self, serializer):
        serializer.save(profile=self.get_user_profile)


class ProfileCreateAPIView(generics.CreateAPIView):
    serializer_class = ProfileModelCreateSerializer
    queryset = queryset
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class ProfileRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileModelRetrieveUpdateSerializer
    queryset = queryset
    permission_classes = [permissions.IsAuthenticated | IsOwnerOrError]
    lookup_field = "username"

    def get_object(self):
        return generics.get_object_or_404(queryset, user__username=self.kwargs.get("username"))

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class ToggleProfileVerification(generics.views.APIView):
    permission_classes = [IsCEO, IsDirector, IsManager]

    def get(self, request, *args, **kwargs):
        user = request.user
        verified = Profile.objects.toggle_verification(user)
        return response.Response(verified, status=status.HTTP_200_OK, headers={})


class SettingsRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return generics.get_object_or_404(Settings.objects.all(), profile__user=self.request.user)

    def get_profile(self):
        return generics.get_object_or_404(Profile.objects.all(), user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(profile=self.get_profile())

    def get(self, request, *args, **kwargs):
        print(self.get_object())
        print(self.get_profile())
        return self.retrieve(self, request, *args, **kwargs)

