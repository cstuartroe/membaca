from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt
from spaced_repetition.models.document import Document
from spaced_repetition.models.language import LANGUAGE_IDS


def heaps_law(x: int):
    return 7*(x**.6)


class Command(BaseCommand):
    help = 'Estimates the function predicting how many words will appear in a corpus of a given size'

    def add_arguments(self, parser):
        parser.add_argument("-l", "--language", required=True)

    def handle(self, *args, **options):
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

        plt.plot(*zip(*points), marker='o')

        max_value = points[-1][0]
        all_xs = list(range(1, max_value+1))
        plt.plot(all_xs, list(map(heaps_law, all_xs)))

        plt.show()
