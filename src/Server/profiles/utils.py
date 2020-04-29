from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import assign_perm


def assign_user_profile(user, _model, admins=[]):
    """
    Assign Object(model) permission for the object's associated
    user and site administrators
    :param user: the object's associated user
    :param _model: the object itself
    :param admins: optional administrators for control and security reasons
    :return: Boolean
    """
    for admin in admins:
        admin_checker = ObjectPermissionChecker(admin)
        admin_has_perm = admin_checker.has_perm("profile_user", _model)
        if not admin_has_perm:
            assign_perm("profile_user", admin, _model)
    checker = ObjectPermissionChecker(user)
    has_perm = checker.has_perm("profile_user", _model)
    if not has_perm:
        assign_perm("profile_user", user, _model)
    return user.has_perm("profile_user", _model)


def profile_image_upload_to(instance, filename):
    return f"profile/{instance.user.username}/picture/{filename}"
