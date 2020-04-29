from django.db.models import Manager, QuerySet
from rest_framework.serializers import ValidationError


class DiscussionQueryset(QuerySet):

    def active(self):
        return self.filter(active=True)

    def by_user(self, user):
        return self.filter(user=user)


class DiscussionManager(Manager):

    def get_queryset(self):
        return DiscussionQueryset(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def filter_by_user(self, user):
        return self.get_queryset().by_user(user)

    def view(self, _model, user):
        if user is not _model.user and user not in _model.views.all():
            _model.views.add(user)
            return True
        return False

    def start(self, user, name):
        obj, created = self.get_or_create(user=user, name=name)
        if not created:
            raise ValidationError({"name": f"Permission denied!. {name} is already being discussed"})
        return obj

    def toggle_activation(self, disc):
        obj = self.get(id=disc.id)
        if obj.active:
            obj.active = False
        obj.active = True
        obj.save()
        return obj, obj.active

    def remove(self, disc):
        obj = self.get(id=disc.id)
        obj.delete()
        return True

    def join(self, user, disc):
        if user not in disc.participants.all() and user is not disc.user:
            disc.participants.add(user)
            disc.save()
            return True
        return False

    def leave(self, user, disc):
        if user in disc.participants.all():
            disc.participants.remove(user)
            disc.save()
            return True
        return False


class ReplyQueryset(QuerySet):

    def by_user(self, user):
        return self.filter(user=user)

    def video_mssgs(self):
        return self.filter(msg_type="Video")

    def sticker_mssgs(self):
        return self.filter(msg_type="Sticker")

    def img_mssgs(self):
        return self.filter(msg_type="Image")

    def audio_mssgs(self):
        return self.filter(msg_type="Audio")

    def text_messages(self):
        return self.filter(msg_type="Text")

    def user_vid_mssg(self, user):
        return self.filter(msg_type="Video", user=user)

    def user_img_mssg(self, user):
        return self.filter(msg_type="Image", user=user)

    def user_aud_mssg(self, user):
        return self.filter(msg_type="Audio", user=user)

    def user_stk_mssg(self, user):
        return self.filter(msg_type="Sticker", user=user)

    def user_text_messages(self, user):
        return self.filter(msg_type="Text", user=user)


class ReplyManager(Manager):

    def get_queryset(self):
        return ReplyQueryset(self.model, using=self._db)

    def reply(self, user, thread, msg=None, vid=None, aud=None, stk=None, img=None, _type="Text"):
        obj = self.model(user=user, thread=thread, msg_type=_type)
        if _type == "Image":
            obj.image = img
        elif _type == "Video":
            obj.video = vid
        elif _type == "Audio":
            obj.audio = aud
        elif _type == "Sticker":
            obj.sticker = stk
        else:
            obj.message = msg
        obj.save()
        return obj

    def delete_message(self, reply):
        obj = self.get(id=reply.id)
        obj.delete()
        return True

    def filter_by_user(self, user):
        return self.get_queryset().by_user(user)

    def filter_by_videos(self):
        return self.get_queryset().video_mssgs()

    def filter_by_audios(self):
        return self.get_queryset().audio_mssgs()

    def filter_by_stickers(self):
        return self.get_queryset().sticker_mssgs()

    def filter_by_images(self):
        return self.get_queryset().img_mssgs()

    def filter_by_texts(self):
        return self.get_queryset().text_messages()

    def filter_by_user_video_msg(self, user):
        return self.get_queryset().user_vid_mssg(user)

    def filter_by_user_audio_msg(self, user):
        return self.get_queryset().user_aud_mssg(user)

    def filter_by_user_sticker_msg(self, user):
        return self.get_queryset().user_stk_mssg(user)

    def filter_by_user_image_msg(self, user):
        return self.get_queryset().user_img_mssg(user)

    def filter_by_user_text_msg(self, user):
        return self.get_queryset().user_text_messages(user)
