from django.db import models
from .lemma import Lemma
from .sentence import Sentence


class WordInSentence(models.Model):
    lemma = models.ForeignKey(Lemma, on_delete=models.CASCADE)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE)


class Substring(models.Model):
    start = models.IntegerField()
    end = models.IntegerField()
    word = models.ForeignKey(WordInSentence, on_delete=models.CASCADE)
