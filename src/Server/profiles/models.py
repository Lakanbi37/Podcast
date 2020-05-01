from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from .utils import profile_image_upload_to, assign_user_profile

# Create your models here.

User = get_user_model()


class AuthorQuerySet(models.QuerySet):

    def verified(self):
        return self.filter(verified=True)

    def unverified(self):
        return self.filter(verified=False)


class AuthorManager(models.Manager):

    def get_queryset(self):
        return AuthorQuerySet(self.model, using=self._db)

    def register(self, user):
        profile, created = self.get_or_create(user=user)
        return profile, created

    def verify_user(self, user):
        obj = get_object_or_404(self.model, user=user)
        if not obj.verified:
            obj.verified = True
            obj.save()
            return True
        return False

    def cancel_user_verification(self, user):
        obj = get_object_or_404(self.model, user=user)
        if obj.verified:
            obj.verified = False
            obj.save()
            return True
        return False

    def filter_by_verified(self):
        return self.get_queryset().verified()

    def filter_by_unverified(self):
        return self.get_queryset().unverified()


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_profile")
    image = models.ImageField(upload_to=profile_image_upload_to, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    d_o_b = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    street = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=120, null=True, blank=True)
    verified = models.BooleanField(default=False)
    joined = models.DateTimeField(auto_now_add=True)

    objects = AuthorManager()

    class Meta:
        permissions = [
            ("c_e_o", _("Chief Executive Officer")),
            ("director", _("Director")),
            ("user_support", _("User Management")),
            ("forum_admin", _("Forum Administrator")),
            ("promoter", _("Promoter")),
            ("profile_user", _("Profile User"))
        ]
        ordering = ["-joined"]

    def __str__(self):
        return str(self.user)


class SocialLink(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    google = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)

    def __str__(self):
        return str(self.profile)


class Settings(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    push_notification = models.BooleanField(verbose_name="Push Notification", default=False)
    sms_notification = models.BooleanField(verbose_name="Sms Notification", default=False)
    email_notification = models.BooleanField(verbose_name="Email Notification", default=True)

    def __str__(self):
        return str(self.profile)


def profile_create_receiver(sender, instance, created, **kwargs):
    if created:
        try:
            profile = Profile.objects.register(instance)
            settings = Settings()
            settings.profile = profile
            settings.save()
            admins = list(User.objects.filter(is_superuser=True))
            assign_user_profile(instance, profile, admins)
        except Exception as e:
            print(str(e))
            pass


post_save.connect(profile_create_receiver, sender=User)
