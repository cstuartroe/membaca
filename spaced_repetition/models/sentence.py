from django.db import models
from .document import Document


class Sentence(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    position = models.IntegerField()
    text = models.CharField(max_length=256)
    translation = models.CharField(max_length=256)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_sentence_position",
                fields=[
                    "document",
                    "position",
                ],
            )
        ]

    def __str__(self):
        return self.text
