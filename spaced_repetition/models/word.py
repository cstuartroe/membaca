from django.db import models
from .language import Language
from .lemma import Lemma


class Word(models.Model):
    """This class represents the mapping from words - i.e.,
    strings that appear in text - to lemmas. It differs from
    WordInSentence in that WordInSentence refers to a single
    appearance of a word in a specific sentence, whereas this
    model refers to something like the word "liked", an
    inflection of the lemma "like", in no particular context.

    This model essentially functions as a search index, and its
    rows can be reconstructed if deleted. They are created by
    a batch indexing job, `manage.py index_words`.
    """

    word = models.CharField(max_length=64)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    lemma = models.ForeignKey(Lemma, on_delete=models.CASCADE)
