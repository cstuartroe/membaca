from django.core.management.base import BaseCommand

from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.word_in_sentence import WordInSentence
from spaced_repetition.models.word import Word


def get_lemma_by_id(lemma_id: int | None):
    if lemma_id is None:
        return None

    lemmas = list(Lemma.objects.filter(id=lemma_id))
    return lemmas[0] if lemmas else None


class Command(BaseCommand):
    help = 'Indexes the words'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        words_and_lemma_ids: set[tuple[str, int, int]] = set()

        print("Loading lemmas...")
        for lemma in Lemma.objects.all():
            words_and_lemma_ids.add(
                (lemma.citation_form, lemma.id, lemma.language_id)
            )

        print("Loading words in sentences...")
        for word_in_sentence in (
                WordInSentence.objects
                        .prefetch_related('substrings')
                        .select_related('sentence')
                        .select_related('sentence__document')
                        .select_related('sentence__document__collection')
                        .all()
        ):
            word = ' '.join(
                word_in_sentence.sentence.text[substring.start:substring.end]
                for substring in word_in_sentence.substrings.all()
            )
            words_and_lemma_ids.add((word, word_in_sentence.lemma_id, word_in_sentence.sentence.document.collection.language_id))

        existing_words_and_lemma_ids: set[tuple[str, int, int]] = set()
        print("Loading existing words...")
        for word in Word.objects.all():
            existing_words_and_lemma_ids.add((word.word, word.lemma_id, word.language_id))

        print("Comparing existing and newly computed words...")
        words_to_create = words_and_lemma_ids - existing_words_and_lemma_ids
        words_to_delete = existing_words_and_lemma_ids - words_and_lemma_ids

        if words_to_create:
            print("- Words to create:")
            for word, lemma_id, language_id in words_to_create:
                print(word, language_id, get_lemma_by_id(lemma_id))

        if words_to_delete:
            print("- Words to delete:")
            for word, lemma_id, language_id in words_to_delete:
                print(word, language_id, get_lemma_by_id(lemma_id))

        if len(words_to_create) == 0 and len(words_to_delete) == 0:
            print("No changes.")
        else:
            agree = input("Continue? enter y: ")
            if agree.lower() == "y":
                for word, lemma_id, language_id in words_to_create:
                    Word(
                        word=word,
                        lemma_id=lemma_id,
                        language_id=language_id,
                    ).save()
                for word, lemma_id, _ in words_to_delete:
                    Word.objects.get(word=word, lemma_id=lemma_id).delete()
