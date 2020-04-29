from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
    SerializerMethodField
)

from ..core import get_model
from ..profile.serializers import ProfileSerializer

Post = get_model("posts", "Post")


class PostCreateSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ('post_type', 'title', 'thumbnail', 'video', 'audio', 'article')

    def create(self, validated_data):
        author = self.context.get("author")
        return Post.objects.post(author=author, title=validated_data["title"], article=validated_data["article"],
                                 _type=validated_data["post_type"], thumbnail=validated_data["thumbnail"],
                                 audio=validated_data["audio"], video=validated_data["video"])


class PostRetrieveUpdateSerializer(ModelSerializer):
    author = ProfileSerializer()
    likes = SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "author", "slug", "post_type", "title", "thumbnail", "video", "audio", "likes", "article", "timestamp",
            "updated")

    def get_likes(self, obj):
        return obj.likes

    def validate_title(self, value):
        if value == "" or value is None:
            raise ValidationError("Title cannot be empty")
        return value

    def validate(self, attrs):
        print("data", attrs)
        if attrs["post_type"] == "AU" and attrs["audio"] is None:
            raise ValidationError({"audio": "Please upload an audio file"})
        elif attrs["post_type"] == "VD" and attrs["video"] is None:
            raise ValidationError({"video": "Please upload a video file"})
        return attrs

    def update(self, instance, validated_data):
        instance.post_type = validated_data.get("post_type", instance.post_type)
        instance.title = validated_data.get("title", instance.title)
        instance.article = validated_data.get("article", instance.article)
        instance.audio = validated_data.get("audio", instance.audio)
        instance.video = validated_data.get("video", instance.video)
        instance.thumbnail = validated_data.get("thumbnail", instance.thumbnail)
        instance.save()
        return instance


class PostListSerializer(ModelSerializer):
    author = ProfileSerializer()
    likes = SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "author", "slug", "post_type", "title", "thumbnail", "video", "audio", "likes", "article", "timestamp",
            "updated")

    def get_likes(self, obj):
        return obj.likes
