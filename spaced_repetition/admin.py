from django.contrib import admin
from spaced_repetition.models.document import Document
from spaced_repetition.models.language import Language
from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.lemma_add import LemmaAdd
from spaced_repetition.models.sentence import Sentence
from spaced_repetition.models.trial import Trial
from spaced_repetition.models.word_in_sentence import WordInSentence


admin.site.register(Document)
admin.site.register(Language)
admin.site.register(Lemma)
admin.site.register(LemmaAdd)
admin.site.register(Sentence)
admin.site.register(Trial)
admin.site.register(WordInSentence)
