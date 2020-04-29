def message_image_path(instance, filename):
    path = f"replies/{instance.user.username}/{instance.user.thread.name}/images/{filename}"
    return path


def message_audio_path(instance, filename):
    path = f"replies/{instance.user.username}/{instance.user.thread.name}/audios/{filename}"
    return path


def message_video_path(instance, filename):
    path = f"replies/{instance.user.username}/{instance.user.thread.name}/videos/{filename}"
    return path


def message_sticker_path(instance, filename):
    path = f"replies/{instance.user.username}/{instance.user.thread.name}/stickers/{filename}"
    return path
