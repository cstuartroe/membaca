from django.contrib.auth.models import User


def user_to_json(user: User):
    return {
        "id": user.id,
        "is_superuser": user.is_superuser,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "date_joined": user.date_joined,
    }
