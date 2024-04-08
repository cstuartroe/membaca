from django.db import models


LANGUAGE_IDS: dict[str, int] = {
    "Dutch": 1,
    "Indonesian": 2,
}


class Language(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.name

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
        }
