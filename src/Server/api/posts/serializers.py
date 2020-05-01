from datetime import datetime

from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
    SerializerMethodField,
    DateTimeField,
    IntegerField,
    Serializer
)
from comments.models import Comment
from ..comments.serializers import CommentDetailSerializer
from ..core import get_model
from ..membership.serializers import MembershipModelSerializer
from ..profile.serializers import ProfileSerializer
from ..user.serializers import UserDisplaySerializer

Post = get_model("posts", "Post")
PostLike = get_model("posts", "PostLike")
PollChoice = get_model("posts", "PollChoice")
Category = get_model("posts", "Category")


class CategoryModelSerializer(ModelSerializer):
    membership_type = MembershipModelSerializer(read_only=True)
    posts = SerializerMethodField()

    class Meta:
        model = Category
        fields = ("name", "membership", "image", "description", "membership_type", "posts")

        write_only_fields = ["membership"]

    def get_membership(self, obj):
        return obj.membership.membership_type

    def create(self, validated_data):
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.membership = validated_data.get("membership", instance.membership)
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.save()
        return instance

    def get_posts(self, obj):
        return PostListSerializer(obj.posts, many=True, context={"request": self.context.get("request")}).data


class CategoryListSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "membership", "image", "description")

        write_only_fields = ["membership"]


class PostLikeModelSerializer(ModelSerializer):
    user = UserDisplaySerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ["reaction", "user"]

    def create(self, validated_data):
        return PostLike.objects.create(**validated_data)


class PollChoiceModelSerializer(ModelSerializer):
    vote_percent = SerializerMethodField(read_only=True)
    voted = SerializerMethodField(read_only=True)
    votes = UserDisplaySerializer(many=True, read_only=True)

    class Meta:
        model = PollChoice
        fields = ("choice", "image", "vote_percent", "voted", "votes")

    def get_vote_percent(self, obj):
        return obj.calculate

    def get_voted(self, obj):
        return obj.voted(user=self.context.get("request").user)

    def create(self, validated_data):
        return PollChoice.objects.add_poll_choice(**validated_data)

    def update(self, instance, validated_data):
        instance.choice = validated_data.get("choice", instance.choice)
        instance.image = validated_data.get("image", instance.image)
        instance.save()


class PollVoteSerializer(Serializer):
    poll_id = IntegerField(required=True)


class PostCreateSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ('post_type', 'parent', 'category', 'title',
                  'thumbnail', 'video', 'audio', 'content', 'poll_expires')

    def create(self, validated_data):
        author = self.context.get("author")
        return Post.objects.post(author=author,
                                 title=validated_data["title"],
                                 content=validated_data["content"],
                                 _type=validated_data["post_type"],
                                 thumbnail=validated_data["thumbnail"],
                                 audio=validated_data["audio"],
                                 video=validated_data["video"],
                                 parent=validated_data["parent"],
                                 expiry=validated_data["poll_expires"],
                                 category=validated_data["category"]
                                 )


class PostRetrieveUpdateSerializer(ModelSerializer):
    author = ProfileSerializer(read_only=True)
    reactions = PostLikeModelSerializer(many=True, read_only=True)
    expires = SerializerMethodField()
    poll_expires = DateTimeField(required=False,
                                 help_text="When does the poll expires. Leaving this field blank automatically sets "
                                           "the expiry to 10 hours")
    reacted = SerializerMethodField()
    comments = SerializerMethodField()

    class Meta:
        model = Post
        fields = ("id",
                  "author", "slug", "post_type", "title", "thumbnail",
                  "video", "audio", "reactions", "content", "timestamp",
                  "updated", "poll_expires", "expires", "reacted", "comments",)

        write_only_fields = ["poll_expires"]

    def get_expires(self, obj):
        if obj.post_type == "poll":
            return obj.poll_expires
        return None

    def get_reacted(self, obj):
        user = self.context.get("user")
        return obj.get_user_reaction(user)

    def get_comments(self, obj):
        qs = Comment.objects.filter_by_instance(obj)
        return CommentDetailSerializer(qs, many=True).data

    def validate(self, attrs):
        print("data", attrs)
        if attrs["post_type"] == "podcast" and attrs["audio"] is None:
            raise ValidationError({"audio": "Please upload an audio file"})
        elif attrs["post_type"] == "highlight" and attrs["video"] is None:
            raise ValidationError({"video": "Please upload an highlight"})
        elif attrs["post_type"] == "article" and attrs["content"] == "":
            raise ValidationError({"content": "Please write an article"})
        return attrs

    def update(self, instance, validated_data):
        """
        serializer update method for editing database entries
        :param validated_data: object
        :type instance: object
        """
        instance.post_type = validated_data.get("post_type", instance.post_type)
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.article)
        instance.audio = validated_data.get("audio", instance.audio)
        instance.video = validated_data.get("video", instance.video)
        instance.thumbnail = validated_data.get("thumbnail", instance.thumbnail)
        instance.poll_expires = validated_data.get("poll_expires", instance.poll_expires)
        instance.save()
        return instance


class PostListSerializer(ModelSerializer):
    author = ProfileSerializer()
    reactions = PostLikeModelSerializer(many=True, read_only=True)
    expires = SerializerMethodField()
    reacted = SerializerMethodField()
    comments = SerializerMethodField()
    can_view = SerializerMethodField()
    audio = SerializerMethodField()
    video = SerializerMethodField()
    content = SerializerMethodField()

    class Meta:
        model = Post
        fields = ("id",
                  "author", "slug", "post_type", "title", "thumbnail",
                  "video", "audio", "content", "timestamp",
                  "updated", "expires", "reactions", "reacted",
                  "comments", "can_view"
                  )

    def get_reacted(self, obj):
        user = self.context["request"].user
        return obj.get_user_reaction(user)

    def get_audio(self, obj):
        if self.check_permission(obj):
            if obj.post_type == "audio":
                return obj.audio.url
            else:
                return None
        return None

    def get_can_view(self, obj):
        user = self.context["request"].user
        return obj.user_has_permission(user)

    def get_video(self, obj):
        if self.check_permission(obj):
            if obj.post_type == "highlight":
                return obj.video.url
            else:
                return None
        return None

    def get_content(self, obj):
        if self.check_permission(obj):
            return obj.content
        return None

    def check_permission(self, obj):
        user = self.context["request"].user
        return obj.user_has_permission(user)

    def get_expires(self, obj):
        if obj.post_type == "poll":
            return obj.poll_expires
        return None

    def get_comments(self, obj):
        qs = Comment.objects.filter_by_instance(obj)
        return CommentDetailSerializer(qs, many=True).data
