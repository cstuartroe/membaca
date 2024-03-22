from django.db import models


class Language(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.name

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
        }
