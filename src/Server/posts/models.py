from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from rest_framework import serializers
from comments.models import Comment
# Create your models here.

from .utils import (
    post_thumbnail_path,
    post_audio_path,
    post_video_path
)


class PostQuerySet(models.QuerySet):

    def audio(self):
        return self.filter(post_type="Audio")

    def video(self):
        return self.filter(post_type="Video")

    def by_author(self, author):
        return self.filter(author=author)

    def by_author_audios(self, author):
        return self.filter(post_type="Audio", author=author)

    def by_author_videos(self, author):
        return self.filter(post_type="Video", author=author)


class PostManager(models.Manager):

    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def filter_by_audios(self):
        return self.get_queryset().audio()

    def filter_by_video(self):
        return self.get_queryset().video()

    def post(self, author, title, article="", _type="Audio", thumbnail=None, audio=None, video=None):
        if title == "":
            raise serializers.ValidationError("Title cannot be empty")
        obj = self.model(author=author, title=title, article=article, post_type=_type)
        if _type == "AU" and audio is None:
            raise serializers.ValidationError({"audio": "Please upload an audio"})
        else:
            obj.audio = audio
        if _type == "VD" and video is None:
            raise serializers.ValidationError({"video": "Please upload a video"})
        else:
            obj.video = video
        if obj.thumbnail is not None:
            obj.thumbnail = thumbnail
        obj.save()
        return obj

    def toggle_like(self, user, post):
        if user in post.liked.all():
            liked = False
            post.liked.remove(user)
        else:
            liked = True
            post.liked.add(user)
        return liked


class Post(models.Model):
    """
    MODEL FOR POSTING PODCAST ###
    """
    AUDIO = 'AU'
    VIDEO = 'VD'
    TYPE_CHOICES = [
        (AUDIO, 'Audio'),
        (VIDEO, 'Video'),
    ]
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE, related_name="posts")
    slug = models.SlugField()
    post_type = models.CharField(max_length=150, choices=TYPE_CHOICES, default=AUDIO)
    title = models.CharField(max_length=200)
    thumbnail = models.ImageField(verbose_name="Cover Image", upload_to=post_thumbnail_path, blank=True, null=True)
    video = models.FileField(upload_to=post_video_path, blank=True, null=True)
    audio = models.FileField(upload_to=post_audio_path, blank=True, null=True)
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="liked")
    article = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = PostManager()

    def __str__(self):
        return self.title

    @property
    def likes(self):
        return self.liked.all().count()

    @property
    def comments(self):
        return Comment.objects.filter_by_instance(self)

    @property
    def get_content_type(self):
        return ContentType.objects.get_for_model(self.__class__)


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Post.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def post_pre_save_receiver(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(post_pre_save_receiver, sender=Post)
