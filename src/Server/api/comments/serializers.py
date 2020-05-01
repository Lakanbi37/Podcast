from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers as ser
from ..core import get_model
from ..user.serializers import UserSerializer
Comment = get_model("comments", "Comment")


def comment_create_func(model_type="post", slug=None, parent_id=None, user=None):
    class CommentCreateSerializer(ser.ModelSerializer):
        class Meta:
            model = Comment
            fields = ('content', 'comment_type', 'media')

        def __init__(self, **kwargs):
            self.model_type = model_type
            self.slug = slug
            self.parent_obj = None
            self.user = user
            if parent_id:
                parent = Comment.objects.get(id=parent_id)
                if parent:
                    self.parent_obj = parent
            super(CommentCreateSerializer, self).__init__(**kwargs)

        def validate(self, attrs):
            model = ContentType.objects.get(model=self.model_type)
            if model is None:
                raise ser.ValidationError(
                    {"object": f"The {self.model_type} you are commenting on does no longer exist"})
            model = model.model_class()
            obj = model.objects.get(slug=self.slug)
            if obj is None:
                raise ser.ValidationError({f"{self.model_type}": "This object does not exist"})

            return attrs

        def create(self, validated_data):
            return Comment.objects.create_by_model_type(
                slug=self.slug,
                content=validated_data["content"],
                comment_type=validated_data["comment_type"],
                media=validated_data["media"],
                parent_obj=self.parent_obj,
                model_type=self.model_type,
                user=self.user
            )

    return CommentCreateSerializer


class CommentChildSerializer(ser.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ('id', 'user', 'content', 'timestamp')


class CommentDetailSerializer(ser.ModelSerializer):
    user = UserSerializer(read_only=True)
    reply_count = ser.SerializerMethodField()
    # content_object_url = ser.SerializerMethodField()
    replies = ser.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "user", "content", "reply_count", "replies", "timestamp")
        read_only_fields = [
            "reply_count",
            "replies",
        ]

    def get_replies(self, obj):
        if obj.is_parent:
            return CommentChildSerializer(obj.children(), many=True).data
        return []

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children().count()
        return 0