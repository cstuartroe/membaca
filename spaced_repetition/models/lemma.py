from django.db import models
from .language import Language


class Lemma(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    citation_form = models.CharField(max_length=32)
    translation = models.CharField(max_length=128)
