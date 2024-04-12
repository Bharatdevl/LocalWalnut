from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse


def _check_superuser(u):
    return not u.is_superuser


is_super_user = user_passes_test(_check_superuser)


def required_login(view_func, *args, **kwargs):
    """This function is used to check the login requirements
    and permissions to access a particular handler.It is a
    decorator wrapper over login_required and user_passes_test
    to check login and superuser.

    Args:
        view_func (callable): view functions

    Returns:
        decorator: returns a wrapped decorator.
    """
    decorated_view_func = login_required(is_super_user(view_func))
    return decorated_view_func
