import datetime
from django.db import models
from django.core import validators
from .lemma_add import LemmaAdd
from .trial import EASINESS_DAYS, get_due_date


class MetadataTrial(models.Model):
    time_created = models.DateTimeField()
    lemma_add = models.ForeignKey(LemmaAdd, on_delete=models.PROTECT)
    metadata_field = models.CharField(max_length=16)
    choices = models.CharField(max_length=256)
    choice = models.CharField(max_length=128)
    correct = models.BooleanField()
    easiness = models.IntegerField(
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(len(EASINESS_DAYS) - 1),
        ]
    )

    def __str__(self):
        return f"Testing {self.metadata_field} of {self.lemma_add} on {self.time_created}"

    def due_date(self) -> datetime.date:
        return get_due_date(self)

    def to_json(self):
        return {
            "metadata_field": self.metadata_field,
            "correct": self.correct,
            "easiness": self.easiness,
        }
