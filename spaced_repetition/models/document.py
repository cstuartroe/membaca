from django.db import models
from .collection import Collection


class Document(models.Model):
    title = models.CharField(max_length=128)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    order = models.IntegerField()
    link = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.title} in {self.collection.title}"

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "collection_id": self.collection_id,
            "link": self.link,
        }
