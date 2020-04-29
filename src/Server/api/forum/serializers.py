from rest_framework import serializers
from ..user.serializers import UserSerializer
from ..core import get_model

Discussion = get_model("forum", "Discussion")


class DiscussionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    views = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()

    class Meta:
        fields = "__all__"
        model = Discussion

    def get_views(self, obj):
        return obj.view_count

    def get_participants(self, obj):
        return obj.participant_count


class DiscussionModelSerializer(DiscussionSerializer):
    class Meta(DiscussionSerializer.Meta):
        fields = ["name"]

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance

    def create(self, validated_data):
        user = self.context.get("user", None)
        if user is None:
            raise serializers.ValidationError(
                {"non_field_error": "Permission denied!. no user is being associated with this discussion"})
        return Discussion.objects.start(user=user, name=validated_data["name"])
