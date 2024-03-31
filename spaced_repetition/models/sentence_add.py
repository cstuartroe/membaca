from django.db import models
from .user import User
from .sentence import Sentence


class SentenceAdd(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name='adds')
    time_created = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_user_and_sentence",
                fields=[
                    "user",
                    "sentence",
                ],
            )
        ]

    def __str__(self):
        return f"User {self.user} read {self.sentence}"
