from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from rest_framework.serializers import ValidationError

# Create your models here.

User = get_user_model()


class CommentManager(models.Manager):

    def all(self):
        return super(CommentManager, self).filter(parent=None)

    def filter_by_instance(self, instance):
        c_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        return super(CommentManager, self).filter(content_type=c_type, object_id=obj_id).filter(parent=None)

    def create_by_model_type(self, app_label, model_type, slug, content, user, parent_obj=None):
        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model_type)
            _model = content_type.model_class()
        except Exception as e:
            print(str(e))
            raise ValidationError({"error": f"{str(e)}"})
        try:
            obj = _model.objects.get(slug=slug)
            instance = self.model(content=content, user=user, content_type=content_type, object_id=obj.id)
            if parent_obj:
                instance.parent = parent_obj
            instance.save()
            return instance
        except Exception as e:
            print(str(e))
            raise ValidationError({"object": f"{str(e)}"})


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return str(self.user.username)

    def children(self):
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True
