from django.urls import path

from .views import *

urlpatterns = [
    path("<int:user_id>/assign-role/", AssignUserRole.as_view()),
]