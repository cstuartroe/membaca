from django.contrib import admin
from spaced_repetition.models.document import Document
from spaced_repetition.models.language import Language
from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.lemma_add import LemmaAdd
from spaced_repetition.models.sentence import Sentence
from spaced_repetition.models.sentence_add import SentenceAdd
from spaced_repetition.models.trial import Trial
from spaced_repetition.models.user_settings import UserSettings
from spaced_repetition.models.word_in_sentence import WordInSentence, Substring
from spaced_repetition.models.word import Word


admin.site.register(Document)
admin.site.register(Language)
admin.site.register(Lemma)
admin.site.register(LemmaAdd)
admin.site.register(Sentence)
admin.site.register(SentenceAdd)
admin.site.register(Trial)
admin.site.register(UserSettings)
admin.site.register(WordInSentence)
admin.site.register(Substring)
admin.site.register(Word)
