from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from .managers import DiscussionManager, ReplyManager
from .utils import *


# Create your models here.


class Discussion(models.Model):
    """
    A DISCUSSION MODEL ---
    A DISCUSSION IS STARTED BY A SIGNED UP USER AT THE SITE'S FORUM
    WHICH OTHER SIGNED UP USERS OF THE SITE'S FORUM CAN PARTICIPATE IN
    A DISCUSSION SHALL HAVE LAID DOWN RULES AND REGULATION WHICH SHALL BE
    ENFORCED BY THE SITE'S ADMINISTRATORS.. VIOLATION OF THESE RULES SHALL BE
    SANCTIONED ACCORDINGLY
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="creator")
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="discussant")
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    views = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="discussion_views")
    pub_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    objects = DiscussionManager()

    def __str__(self):
        return self.name

    @property
    def view_count(self):
        return self.views.all().count()

    @property
    def participant_count(self):
        return self.participants.all().count()


class Reply(models.Model):
    """
    A REPLY TO A ON GOING DISCUSSION WHICH IS OF THREE TYPES
        - A USER MIGHT SEND AN IMAGE IN REPLY TO A DISCUSSION
        - A USER MIGHT SEND A STICKER IN REPLY TO A DISCUSSION
        - A USER MIGHT SEND A MESSAGE IN REPLY
    A USER WHO IS NOT A PARTICIPANT OF A DISCUSSION WOULD NOT BE ABLE TO MAKE
    CONTRIBUTIONS IN AN ON GOING DISCUSSION
    """
    IMAGE = _('IMG')
    VIDEO = _('VDO')
    STICKER = _('STK')
    TEXT = _('TXT')
    AUDIO = _("AUD")
    TYPE_CHOICES = [
        (IMAGE, _('Image')),
        (VIDEO, _('Video')),
        (STICKER, _('Sicker')),
        (TEXT, _('Text')),
        (AUDIO, _('Audio'))
    ]
    msg_type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    thread = models.ForeignKey(Discussion, null=True, blank=True, related_name="replies", on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(null=True, blank=True)
    video = models.FileField(upload_to=message_video_path, blank=True, null=True)
    image = models.ImageField(upload_to=message_image_path, null=True, blank=True)
    sticker = models.ImageField(upload_to=message_sticker_path, null=True, blank=True)
    audio = models.FileField(upload_to=message_audio_path, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ReplyManager()

    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = "Replies"
        ordering = ["-timestamp"]

    def __str__(self):
        return self.thread


def create_slug(instance, new_slug=None):
    slug = slugify(instance.name)
    if new_slug is not None:
        slug = new_slug
    qs = Discussion.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def discussion_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(discussion_pre_save_receiver, sender=Discussion)
