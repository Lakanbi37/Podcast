def post_thumbnail_path(instance, filename):
    path = f"posts/{instance.author.user.username}/thumbnails/{filename}"
    return path


def post_audio_path(instance, filename):
    path = f"posts/{instance.author.user.username}/audios/{filename}"
    return path


def post_video_path(instance, filename):
    path = f"posts/{instance.author.user.username}/videos/{filename}"
    return path
