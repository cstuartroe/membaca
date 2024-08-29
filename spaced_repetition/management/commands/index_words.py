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
        words_and_lemma_ids: dict[tuple[str, int, int], int] = {}

        print("Loading lemmas...")
        for lemma in Lemma.objects.all():
            words_and_lemma_ids[(lemma.citation_form, lemma.id, lemma.language_id)] = 0

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
            key = (word, word_in_sentence.lemma_id, word_in_sentence.sentence.document.collection.language_id)
            words_and_lemma_ids[key] = words_and_lemma_ids.get(key, 0) + 1

        existing_words_and_lemma_ids: dict[tuple[str, int, int], Word] = {}
        print("Loading existing words...")
        for word in Word.objects.all():
            existing_words_and_lemma_ids[(word.word, word.lemma_id, word.language_id)] = word

        print("Comparing existing and newly computed words...")
        words_to_create = set(words_and_lemma_ids.keys()) - set(existing_words_and_lemma_ids.keys())
        words_to_delete = set(existing_words_and_lemma_ids.keys()) - set(words_and_lemma_ids.keys())
        words_to_update_count = {}
        for key, word in existing_words_and_lemma_ids.items():
            if key not in words_and_lemma_ids:
                continue

            old_count = word.occurrences
            new_count = words_and_lemma_ids[key]
            if old_count != new_count:
                words_to_update_count[key] = word, new_count

        any_updates = False

        if words_to_create:
            any_updates = True
            print("- Words to create:")
            for word, lemma_id, language_id in words_to_create:
                print(word, language_id, get_lemma_by_id(lemma_id))

        if words_to_delete:
            any_updates = True
            print("- Words to delete:")
            for word, lemma_id, language_id in words_to_delete:
                print(word, language_id, get_lemma_by_id(lemma_id))

        if words_to_update_count:
            any_updates = True
            print("- Words to update count")
            for (word, lemma_id, language_id), (word, new_count) in words_to_update_count.items():
                print(word, language_id, get_lemma_by_id(lemma_id), word.occurrences, "->", new_count)

        if not any_updates:
            print("No changes.")
        else:
            agree = input("Continue? enter y: ")
            if agree.lower() == "y":
                for word, lemma_id, language_id in words_to_create:
                    Word(
                        word=word,
                        lemma_id=lemma_id,
                        language_id=language_id,
                        occurrences=0,
                    ).save()

                for word, lemma_id, _ in words_to_delete:
                    Word.objects.get(word=word, lemma_id=lemma_id).delete()

                for word, new_count in words_to_update_count.values():
                    word.occurrences = new_count
                    word.save()
