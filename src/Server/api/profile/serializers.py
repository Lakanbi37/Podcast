from rest_framework.serializers import (
    ModelSerializer,
    ValidationError
)
from ..core import get_model
from ..user.serializers import UserSerializer

Profile = get_model("profiles", "Profile")
SocialLinks = get_model("profiles", "SocialLink")
Settings = get_model("profiles", "Settings")


class ProfileModelSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

    def validate(self, attrs):
        if len(attrs["phone"]) < 11 or len(attrs["phone"]) > 13:
            raise ValidationError({"phone": "Please fill in a correct phone number"})
        elif attrs["street"] != "" and attrs["city"] == "":
            raise ValidationError({"city": "City cannot be blank"})
        elif attrs["city"] != "" and attrs["street"] == "":
            raise ValidationError({"street": "Street cannot be blank"})
        elif attrs["city"] != "" and attrs["country"] == "":
            raise ValidationError({"country": "Country cannot be blank"})
        return attrs


class ProfileModelCreateSerializer(ProfileModelSerializer):
    class Meta(ProfileModelSerializer.Meta):
        fields = ("bio", "d_o_b", "phone", "street", "city", "country",)

    def create(self, validated_data):
        return Profile.objects.create(**validated_data)


class ProfileSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ["user"]


class ProfileModelRetrieveUpdateSerializer(ProfileModelSerializer):
    class Meta(ProfileModelSerializer.Meta):
        fields = ("id", "bio", "d_o_b", "phone", "street", "city", "country", "joined", "verified",)

    def update(self, instance, validated_data):
        instance.bio = validated_data.get("bio", instance.bio)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.d_o_b = validated_data.get("d_o_b", instance.d_o_b)
        instance.street = validated_data.get("street", instance.street)
        instance.city = validated_data.get("city", instance.city)
        instance.country = validated_data.get("country", instance.country)
        instance.save()
        return instance


class SocialLinkSerializer(ModelSerializer):
    class Meta:
        model = SocialLinks
        fields = ("id", "facebook", "twitter", "google", "linkedin", "instagram")

    def create(self, validated_data):
        return SocialLinks.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.facebook = validated_data.get("facebook", instance.facebook)
        instance.twitter = validated_data.get("twitter", instance.twitter)
        instance.google = validated_data.get("google", instance.google)
        instance.linkedin = validated_data.get("linkedin", instance.linkedin)
        instance.instagram = validated_data.get("instagram", instance.instagram)
        instance.save()
        return instance


class SettingsSerializer(ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = Settings
        fields = "__all__"
