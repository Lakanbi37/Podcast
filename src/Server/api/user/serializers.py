from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework import serializers as ser
from ..core import get_model

Discussion = get_model("forum", "Discussion")

User = get_user_model()


class PermissionSerializer(ser.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class UserModelSerializer(ser.ModelSerializer):
    user_permissions = PermissionSerializer(many=True)
    is_authenticated = ser.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name",
                  "last_name", "date_joined", "last_login", "user_permissions",
                  "is_authenticated"
                  ]

    def get_is_authenticated(self, obj):
        """
        :param obj:
        :return: Bool
        """
        return self.context.get("request").user.is_authenticated


class UserSerializer(UserModelSerializer):
    class Meta(UserModelSerializer.Meta):
        fields = ("email", "username", "first_name", "last_name", "last_login")


class UserDiscussionSerializer(ser.ModelSerializer):
    views = UserSerializer(many=True)
    replies = ser.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = "__all__"

    def get_replies(self, obj):
        return obj.replies.all().count()
