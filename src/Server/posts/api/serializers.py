from rest_framework.serializers import (
    ModelSerializer,
    ValidationError
)

from ..models import Post


class PostCreateSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ('post_type', 'title', 'thumbnail', 'video', 'audio', 'article')


    def validate_title(self, value):
        if value == "" or value is None:
            raise ValidationError("Title cannot be empty")
        print(self.validated_data["post_type"])
        return value

    def create(self, validated_data):
        author = self.context.get("author")
        return Post.objects.post(author=author, title=validated_data["title"], article=validated_data["article"],
                                 _type=validated_data["post_type"], thumbnail=validated_data["thumbnail"],
                                 audio=validated_data["audio"], video=validated_data["video"])


class PostRetrieveUpdateSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"

    def validate_title(self, value):
        if value == "" or value is None:
            raise ValidationError("Title cannot be empty")
        return value

    def validate(self, attrs):
        print(attrs)
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
    class Meta:
        model = Post
        fields = "__all__"