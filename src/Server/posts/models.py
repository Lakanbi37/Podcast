import datetime
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from comments.models import Comment
from memberships.models import Membership, UserMembership
# Create your models here.

from .utils import (
    post_thumbnail_path,
    post_audio_path,
    post_video_path
)

now = timezone.now()


def category_upload_to(instance, filename):
    name, ext = filename.split(".")
    return f"categories/{instance.name}/_{name}{now.strftime('%H%M%S.%f')}_.{ext}"


class Category(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    slug = models.SlugField()
    name = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=category_upload_to, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = create_slug(self, self.name)
        super(Category, self).save(*args, **kwargs)

    @property
    def posts(self):
        return self.post_set.all()


class PostQuerySet(models.QuerySet):

    def podcasts(self):
        return self.filter(post_type="podcast")

    def highlights(self):
        return self.filter(post_type="highlight")

    def articles(self):
        return self.filter(post_type="article")

    def polls(self):
        return self.filter(post_type="poll")

    def by_author(self, author):
        return self.filter(author=author)

    def by_author_audios(self, author):
        return self.filter(post_type="podcast", author=author)

    def by_author_videos(self, author):
        return self.filter(post_type="highlight", author=author)


class PostManager(models.Manager):

    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def filter_by_podcast(self):
        return self.get_queryset().podcasts()

    def filter_by_highlight(self):
        return self.get_queryset().highlights()

    def filter_by_poll(self):
        return self.get_queryset().polls()

    def filter_by_article(self):
        return self.get_queryset().articles()

    def post(self, author, title, content="", _type="podcast", category=None, parent=None,
             thumbnail=None, audio=None, video=None, expiry=None):
        if title == "":
            raise serializers.ValidationError({"title": "Title cannot be empty"})
        if category is None:
            raise serializers.ValidationError({"category": "Please add a category"})
        obj = self.model(author=author, title=title,
                         post_type=_type, category=category,
                         timestamp=timezone.now())
        if parent is not None:
            obj.parent = parent
        if obj.post_type == "podcast" and audio is None:
            raise serializers.ValidationError({"audio": "Please upload an audio"})
        else:
            obj.audio = audio
        if obj.post_type == "highlight" and video is None:
            raise serializers.ValidationError({"video": "Please upload a video"})
        else:
            obj.video = video
        if obj.post_type == "article" and content == "":
            raise serializers.ValidationError({"article": "Please write an article"})
        else:
            obj.content = content
        if obj.post_type == "poll" and content == "":
            raise serializers.ValidationError({"question": "Please ask a question"})
        else:
            default_expiry = obj.timestamp + datetime.timedelta(hours=10)
            obj.poll_expiry = default_expiry if expiry == "" else expiry
        if obj.thumbnail is not None:
            obj.thumbnail = thumbnail
        obj.save()
        return obj


class Post(models.Model):
    """
    MODEL FOR POSTING PODCAST ###
    """
    PODCAST = 'podcast'
    HIGHLIGHT = 'highlight'
    POLL = 'poll'
    ARTICLE = 'article'
    TYPE_CHOICES = [
        (PODCAST, _('Podcast')),
        (HIGHLIGHT, _('Highlight')),
        (POLL, _('Poll')),
        (ARTICLE, _('Article'))
    ]
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE, related_name="posts")
    slug = models.SlugField()
    post_type = models.CharField(max_length=150, choices=TYPE_CHOICES, default=PODCAST)
    title = models.CharField(max_length=200)
    thumbnail = models.ImageField(verbose_name="Cover Image", upload_to=post_thumbnail_path, blank=True, null=True)
    video = models.FileField(upload_to=post_video_path, blank=True, null=True)
    audio = models.FileField(upload_to=post_audio_path, blank=True, null=True)
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                   through="PostLike", through_fields=('post', 'user'),
                                   related_name="liked")
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    poll_expires = models.DateTimeField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = PostManager()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return self.title

    @property
    def likes(self):
        return self.liked.all().count()

    def user_has_permission(self, user):
        try:
            user_membership = UserMembership.objects.get(user=user)
        except Exception as e:
            return False
        return bool(user_membership.membership == self.category.membership)

    def get_user_reaction(self, user):
        try:
            reaction = self.reactions.get(user=user)
            print(reaction)
            if user in self.liked.all():
                return True
        except Exception as e:
            return False

    @property
    def comments(self):
        return Comment.objects.filter_by_instance(self)

    @property
    def get_content_type(self):
        return ContentType.objects.get_for_model(self.__class__)

    @property
    def poll_choices(self):
        return PollChoice.objects.filter_by_post(post_id=self.id)

    @property
    def poll_votes(self):
        qs = PollChoice.objects.filter_by_post(post_id=self.id)
        _votes = 0
        for q in qs:
            _votes += int(q.votes.all().count())
        return _votes

    @property
    def poll_voters(self):
        queryset = PollChoice.objects.filter_by_post(post_id=self.id)
        voters = []
        for query in queryset:
            for user in query.votes.all():
                voters.append(user)
        print(voters)
        return voters

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True


def create_slug(instance, field, new_slug=None):
    slug = slugify(field)
    if new_slug is not None:
        slug = new_slug
    model = instance.__class__
    qs = model.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = f"{slug}-{datetime.datetime.now(datetime.timezone.utc).strftime('%H_%M_%S_%f')}"
        return create_slug(instance, field, new_slug=new_slug)
    return slug


def post_pre_save_receiver(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance, instance.title)


pre_save.connect(post_pre_save_receiver, sender=Post)


class PostLike(models.Model):
    LIKE = _("like")
    LOVE = _("love")
    HAPPY = _("happy")
    SAD = _("sad")
    ANGRY = _("angry")
    FUNNY = _("funny")
    DISLIKE = _("dislike")
    REACTIONS = (
        (LIKE, _("Like")),
        (LOVE, _("Love")),
        (SAD, _("Sad")),
        (ANGRY, _("Angry")),
        (HAPPY, _("Happy")),
        (FUNNY, _("Funny")),
        (DISLIKE, _("Dislike"))
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=20, choices=REACTIONS, default=LIKE)

    def __str__(self):
        return str(self.reaction)


class PollQuerySet(models.QuerySet):

    def filter_by_post(self, post_id):
        return self.filter(post__id=post_id)


class PollsManager(models.Manager):

    def get_queryset(self):
        return PollQuerySet(self.model, using=self._db)

    def filter_by_post(self, post_id):
        return self.get_queryset().filter_by_post(post_id)

    def calculate(self, poll_id):
        poll = self.get(id=poll_id)
        total_votes = poll.post.poll_votes
        try:
            return int(poll.votes.count()) / total_votes * 100
        except ZeroDivisionError:
            return 0

    def vote(self, poll_id, user):
        try:
            poll = self.get(id=poll_id)
        except Exception:
            raise serializers.ValidationError({"poll": "Poll does not exist"})
        post = poll.post
        if user not in post.poll_voters:
            poll.votes.add(user)
            poll.save()
            return True
        return False

    def add_poll_choice(self, choice, post_id=None, image=None):
        if post_id is not None:
            try:
                post = Post.objects.get(id=post_id)
            except Exception as e:
                raise serializers.ValidationError({"post": "Post does not exist"})
        else:
            raise serializers.ValidationError({"post": "This field is required"})
        poll_choice = self.model(post=post, choice=choice)
        if image is not None:
            poll_choice.image = image
        poll_choice.save()
        return poll_choice


def poll_upload_to(instance, filename):
    file, ext = filename.split(".")
    return f"poll/{instance.post.title}/{instance.choice}/{now.strftime('%H%M%S.%f')}_{file}_.{ext}"


class PollChoice(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="poll")
    choice = models.CharField(max_length=120)
    image = models.ImageField(upload_to=poll_upload_to, null=True, blank=True)
    votes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = PollsManager()

    def __str__(self):
        return str(self.post)

    def voted(self, user):
        return bool(user in self.votes.all())

    @property
    def calculate(self):
        try:
            return int(self.votes.count()) / self.post.poll_votes * 100
        except ZeroDivisionError:
            return 0
