from django.db import models
from .lemma import Lemma
from .sentence import Sentence


class WordInSentence(models.Model):
    # Null lemma should be used for proper nouns, numbers written
    # as digits, etc.
    lemma = models.ForeignKey(Lemma, on_delete=models.CASCADE, null=True)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE)

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "lemma_id": self.lemma.id,
            "sentence_id": self.sentence.id,
        }


class Substring(models.Model):
    start = models.IntegerField()
    end = models.IntegerField()
    word = models.ForeignKey(WordInSentence, on_delete=models.CASCADE, related_name='substrings')

    def to_json(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
            # skip word, it's usually joined
        }
