from django.db import models
from .language import Language


class Document(models.Model):
    title = models.CharField(max_length=128)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    link = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.title} in {self.language.name}"

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "language": self.language.id,
            "link": self.link,
        }
