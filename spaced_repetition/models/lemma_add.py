from django.db import models
from django.contrib.auth.models import User
from .lemma import Lemma


class LemmaAdd(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    lemma = models.ForeignKey(Lemma, on_delete=models.PROTECT)
    time_created = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_user_and_lemma",
                fields=[
                    "user",
                    "lemma",
                ],
            )
        ]

    def __str__(self):
        return f"User {self.user} playing {self.lemma}"
