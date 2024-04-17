import datetime
from django.db import models
from django.core import validators
from django.utils.translation import gettext_lazy as _
from .lemma_add import LemmaAdd
from .sentence import Sentence


EASINESS_DAYS = [
    0,
    1,
    2,
    4,
    10,
    30,
    90,
    365,
]


MAX_EASINESS = len(EASINESS_DAYS) - 1


class Trial(models.Model):
    class TrialType(models.TextChoices):
        CLOZE = "cz", _("cloze")
        CHOOSE_TRANSLATION = "ct", _("choose translation")
        CHOOSE_CITATION_FORM = "cc", _("choose citation form")

    time_created = models.DateTimeField()
    lemma_add = models.ForeignKey(LemmaAdd, on_delete=models.PROTECT)
    trial_type = models.CharField(max_length=2, choices=TrialType.choices)
    sentence = models.ForeignKey(Sentence, null=True, blank=True, on_delete=models.PROTECT)
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
        return f"{self.lemma_add} on {self.time_created}"

    def due_date(self) -> datetime.date:
        return (self.time_created + datetime.timedelta(days=EASINESS_DAYS[self.easiness])).date()

    def to_json(self):
        return {
            "trial_type": self.trial_type,
            "correct": self.correct,
            "easiness": self.easiness,
        }
