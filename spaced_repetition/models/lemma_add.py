from django.db import models
from django.contrib.auth.models import User
from .lemma import Lemma


class LemmaAdd(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lemma = models.ForeignKey(Lemma, on_delete=models.CASCADE)
    time_created = models.DateTimeField()

    def __str__(self):
        return f"User {self.user} playing {self.lemma}"
