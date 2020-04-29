from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import (Serializer, ModelSerializer, ValidationError,
                                        ChoiceField)
from ..core import get_model
Profile = get_model("profiles", "Profile")

PERM_CHOICES = (
    ('', _('--Choose User Permission--')),
    ("c_e_o", _("Chief Executive Officer")),
    ("director", _("Director")),
    ("user_support", _("User Management")),
    ("forum_admin", _("Forum Administrator")),
    ("promoter", _("Promoter")),
)


class PermissionSerializer(Serializer):
    role = ChoiceField(choices=PERM_CHOICES, label=_("Assign role"), initial='promoter')

    def validate(self, attrs):
        if attrs["role"] == "":
            raise ValidationError({"role": "Please choose a user role"})
        return attrs


class ProfileListSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
