from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt
from spaced_repetition.models.document import Document
from spaced_repetition.models.language import LANGUAGE_IDS


def heaps_law(x: int):
    return 5.1*(x**.63)


class Command(BaseCommand):
    help = 'Estimates the function predicting how many words will appear in a corpus of a given size'

    def add_arguments(self, parser):
        parser.add_argument("-l", "--language", required=True)

    def handle(self, *args, **options):
        for word_count in [100000, 250000, 1000000]:
            print(f"Projected lemma count at {word_count} words read: {round(heaps_law(word_count))}")

        lemma_ids = set()
        num_words = 0
        points = []

        for document in (
            Document.objects
            .select_related('collection')
            .filter(collection__language_id=LANGUAGE_IDS[options["language"]])
            .order_by('id')
            .prefetch_related('sentence_set')
            .prefetch_related('sentence_set__words_in_sentence')
        ):
            for sentence in document.sentence_set.order_by('position'):
                for word in sentence.words_in_sentence.all():
                    num_words += 1
                    lemma_ids.add(word.lemma_id)

                points.append((num_words, len(lemma_ids)))

        actual_num_words, actual_lemmas = points[-1]
        all_xs = list(range(1, actual_num_words+1))
        print(f"Projected lemma count at current word count ({actual_num_words}): {round(heaps_law(actual_num_words))}")
        print(f"Actual lemma count: {actual_lemmas}")

        plt.plot(*zip(*points), marker='o')
        plt.plot(all_xs, list(map(heaps_law, all_xs)))
        plt.show()
