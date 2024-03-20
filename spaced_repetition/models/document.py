from django.db import models
from .language import Language


class Document(models.Model):
    title = models.CharField(max_length=128)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    link = models.CharField(max_length=256)
