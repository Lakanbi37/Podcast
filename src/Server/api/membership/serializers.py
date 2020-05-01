from rest_framework.serializers import ModelSerializer, DecimalField, SlugField

from memberships.models import Membership


class MembershipModelSerializer(ModelSerializer):
    price = DecimalField(write_only=True, max_digits=100, decimal_places=2)
    slug = SlugField(read_only=True)

    class Meta:
        model = Membership
        fields = ("membership_type", "slug", "price")

    def create(self, validated_data):
        return Membership.objects.create(**validated_data)