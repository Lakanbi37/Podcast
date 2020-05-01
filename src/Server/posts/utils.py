from django.utils import timezone

now = timezone.now()


def post_thumbnail_path(instance, filename):
    path = f"posts/{instance.category.slug}/thumbnails/_{now.strftime('%H_%M_%S.%f')}_{filename}"
    return path


def post_audio_path(instance, filename):
    path = f"posts/{instance.category.slug}/audios/_{now.strftime('%H_%M_%S.%f')}_{filename}"
    return path


def post_video_path(instance, filename):
    path = f"posts/{instance.category.slug}/videos/_{now.strftime('%H_%M_%S.%f')}_{filename}"
    return path
