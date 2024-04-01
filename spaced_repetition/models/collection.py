from django.db import models
from .language import Language


class Collection(models.Model):
    title = models.CharField(max_length=64)
    language = models.ForeignKey(Language, on_delete=models.PROTECT)

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "language_id": self.language_id,
        }
