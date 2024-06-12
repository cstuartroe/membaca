import re
from dataclasses import dataclass
from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt
from spaced_repetition.models.collection import Collection
from spaced_repetition.models.document import Document
from spaced_repetition.models.language import LANGUAGE_IDS


def heaps_law(x: int):
    return 5.1*(x**.63)


@dataclass
class CollectionSummary:
    num_annotated_words: int
    num_unique_annotated_lemmas: int
    num_whitespace_words: int
    num_unique_whitespace_words: int


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

        collection_summaries = {}

        for document in (
            Document.objects
            .select_related('collection')
            .filter(collection__language_id=LANGUAGE_IDS[options["language"]])
            .order_by('id')
            .prefetch_related('sentence_set')
            .prefetch_related('sentence_set__words_in_sentence')
        ):
            document_annotated_word_lemma_ids = []
            document_whitespace_words = []

            for sentence in document.sentence_set.order_by('position'):
                document_whitespace_words += list(re.findall("\\w+", sentence.text))

                for word in sentence.words_in_sentence.order_by('id'):
                    num_words += 1
                    lemma_ids.add(word.lemma_id)
                    points.append((num_words, len(lemma_ids)))

                    document_annotated_word_lemma_ids.append(word.lemma_id)

            if document.collection_id not in collection_summaries:
                collection_summaries[document.collection_id] = CollectionSummary(0, 0, 0, 0)

            summary = collection_summaries[document.collection_id]
            summary.num_annotated_words += len(document_annotated_word_lemma_ids)
            summary.num_unique_annotated_lemmas += len(set(document_annotated_word_lemma_ids))
            summary.num_whitespace_words += len(document_whitespace_words)
            summary.num_unique_whitespace_words += len(set(document_whitespace_words))

        actual_num_words, actual_lemmas = points[-1]
        all_xs = list(range(1, actual_num_words+1))
        print(f"Projected lemma count at current word count ({actual_num_words}): {round(heaps_law(actual_num_words))}")
        print(f"Actual lemma count: {actual_lemmas}")

        for collection_id, summary in collection_summaries.items():
            print()
            print(f"Collection {Collection.objects.get(id=collection_id).title}:")
            print(f"{summary.num_annotated_words} words according to annotation.")
            print(f"{summary.num_whitespace_words} words according to whitespace.")
            print(f"{summary.num_unique_annotated_lemmas} unique lemmas according to annotation.")
            print(f"{summary.num_unique_whitespace_words} unique words according to whitespace.")

        plt.plot(*zip(*points))
        plt.plot(all_xs, list(map(heaps_law, all_xs)))
        plt.show()
