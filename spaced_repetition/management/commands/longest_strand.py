from django.core.management.base import BaseCommand

from spaced_repetition.models.word_in_sentence import WordInSentence
from .usages import print_highlighted_word_in_sentence


class Command(BaseCommand):
    help = 'Finds the furthest-stranded substrings in the corpus'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        words_and_distances: list[tuple[int, WordInSentence]] = []

        print("Loading words in sentences...")
        for word_in_sentence in (
                WordInSentence.objects
                        .prefetch_related('substrings')
                        .select_related('sentence')
                        .select_related('sentence__document')
                        .select_related('sentence__document__collection')
                        .all()
        ):
            substring_starts = [
                substring.start
                for substring in word_in_sentence.substrings.all()
            ]
            if len(substring_starts) == 0:
                print("Lacking substrings")
                print(word_in_sentence.id)
                print(list(word_in_sentence.substrings.all()))
                continue
            words_and_distances.append((max(substring_starts) - min(substring_starts), word_in_sentence))

        words_and_distances.sort(key=lambda x: -x[0])

        for distance, word in words_and_distances[:10]:
            print(distance)
            print_highlighted_word_in_sentence(word)

