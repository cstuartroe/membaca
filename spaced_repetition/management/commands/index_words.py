from django.core.management.base import BaseCommand

from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.sentence import Sentence
from spaced_repetition.models.word_in_sentence import WordInSentence
from spaced_repetition.models.word import Word


class Command(BaseCommand):
    help = 'Indexes the words'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        words_and_lemma_ids: set[tuple[str, int]] = set()
        lemma_ids_to_language_ids: dict[int, int] = {}

        for lemma in Lemma.objects.all():
            lemma_ids_to_language_ids[lemma.id] = lemma.language_id
            words_and_lemma_ids.add(
                (lemma.citation_form, lemma.id)
            )

        for word_in_sentence in WordInSentence.objects.prefetch_related('substrings').select_related('sentence').all():
            word = ' '.join(
                word_in_sentence.sentence.text[substring.start:substring.end]
                for substring in word_in_sentence.substrings.all()
            )
            words_and_lemma_ids.add((word, word_in_sentence.lemma_id))

        Word.objects.all().delete()
        for word, lemma_id in words_and_lemma_ids:
            Word(
                word=word,
                lemma_id=lemma_id,
                language_id=lemma_ids_to_language_ids[lemma_id],
            ).save()
