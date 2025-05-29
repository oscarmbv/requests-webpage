# tasks/context_processors.py
from .views import is_admin, is_leadership

def user_role_permissions(request):
    is_admin_user_ctx = False
    is_leadership_user_ctx = False
    if request.user.is_authenticated:
        is_admin_user_ctx = is_admin(request.user)
        is_leadership_user_ctx = is_leadership(request.user)
    return {
        'is_admin_user': is_admin_user_ctx,
        'is_leadership_user': is_leadership_user_ctx,
    }