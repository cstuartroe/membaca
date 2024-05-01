from django.db import models
from django.contrib.auth.models import User
from .language import Language


class UserSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    current_language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
