import uuid
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from datetime import datetime

# import stripe
# stripe.api_key = settings.STRIPE_SECRET_KEY


class Membership(models.Model):
    FREE = _("free")
    PRO = _("pro")
    MEMBERSHIP_CHOICES = (
        (FREE, _("Free")),
        (PRO, _("Pro"))
    )
    slug = models.SlugField()
    membership_type = models.CharField(
        choices=MEMBERSHIP_CHOICES,
        default=FREE,
        max_length=30)
    price = models.IntegerField(default=15)

    # stripe_plan_id = models.CharField(max_length=40)

    def __str__(self):
        return self.membership_type

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.membership_type)
        super(Membership, self).save(*args, **kwargs)


class UserMembership(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=40)
    membership = models.ForeignKey(
        Membership, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username


def post_save_usermembership_create(sender, instance, created, *args, **kwargs):
    if created:
        user_membership, created = UserMembership.objects.get_or_create(
            user=instance)

        if user_membership.customer_id is None or user_membership.customer_id == '':
            new_customer_id = str(uuid.uuid4())
            free_membership, created = Membership.objects.get_or_create(membership_type='free')
            user_membership.stripe_customer_id = new_customer_id
            user_membership.membership = free_membership
            user_membership.save()


post_save.connect(post_save_usermembership_create,
                  sender=settings.AUTH_USER_MODEL)


class Subscription(models.Model):
    user_membership = models.ForeignKey(
        UserMembership, on_delete=models.CASCADE)
    subscription_id = models.CharField(max_length=40)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user_membership.user.username

    # @property
    # def get_created_date(self):
    #     subscription = stripe.Subscription.retrieve(
    #         self.stripe_subscription_id)
    #     return datetime.fromtimestamp(subscription.created)

    # @property
    # def get_next_billing_date(self):
    #     subscription = stripe.Subscription.retrieve(
    #         self.stripe_subscription_id)
    #     return datetime.fromtimestamp(subscription.current_period_end)
