from django.db import models
from django.utils.translation import gettext_lazy as _
from .document import Document


class Sentence(models.Model):
    document = models.ForeignKey(Document, on_delete=models.PROTECT)
    position = models.IntegerField()
    text = models.TextField()
    translation = models.TextField()
    # URL to an image that will be displayed above the sentence
    image = models.CharField(max_length=256, blank=True)

    class FormatLevel(models.TextChoices):
        H1 = "h1", _("h1")
        H2 = "h2", _("h2")
        H3 = "h3", _("h3")
        P = "p", _("p")
        NEW_SECTION = "ns", _("new section")

    format_level = models.CharField(
        max_length=2,
        choices=FormatLevel.choices,
        default=FormatLevel.P,
    )

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

    def to_json(self):
        # document and position are not expected to be included,
        # since they are usually just used for orders and joins
        return {
            "id": self.id,
            "text": self.text,
            "translation": self.translation,
            "image": self.image or None,
            "format_level": self.format_level,
        }
