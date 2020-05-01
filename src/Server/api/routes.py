from django.urls import path, include

urlpatterns = [
    path("comments/", include("api.comments")),
    path("dashboard/", include("api.dashboard")),
    path("forum/", include("api.forum")),
    path("memberships/", include("api.membership")),
    path("posts/", include("api.posts")),
    path("profile/", include("api.profile")),
    path("user/", include("api.user")),
]