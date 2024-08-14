import re
from dataclasses import dataclass
from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt
from spaced_repetition.models.collection import Collection
from spaced_repetition.models.document import Document
from spaced_repetition.models.language import LANGUAGE_IDS


def heaps_law(x: int):
    return 6*(x**.63)


@dataclass
class WordCountSummary:
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

        collection_lemma_ids = {}
        collection_whitespace_words = {}
        document_summaries = {}

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

            sentences = list(document.sentence_set.all())
            sentences.sort(key=lambda s: s.position)

            for sentence in sentences:
                document_whitespace_words += list(re.findall("\\w+", sentence.text))

                words = list(sentence.words_in_sentence.all())
                words.sort(key=lambda w: w.id)

                for word in words:
                    num_words += 1

                    if word.lemma_id is not None:
                        lemma_ids.add(word.lemma_id)
                        document_annotated_word_lemma_ids.append(word.lemma_id)

                    points.append((num_words, len(lemma_ids)))

            document_summaries[document.title] = WordCountSummary(
                num_annotated_words=len(document_annotated_word_lemma_ids),
                num_unique_annotated_lemmas =len(set(document_annotated_word_lemma_ids)),
                num_whitespace_words=len(document_whitespace_words),
                num_unique_whitespace_words=len(set(document_whitespace_words)),
            )

            if document.collection_id not in collection_lemma_ids:
                collection_lemma_ids[document.collection_id] = []
                collection_whitespace_words[document.collection_id] = []
            collection_lemma_ids[document.collection_id] += document_annotated_word_lemma_ids
            collection_whitespace_words[document.collection_id] += document_whitespace_words

        collection_summaries = {
            collection_id: WordCountSummary(
                num_annotated_words=len(lemma_ids),
                num_unique_annotated_lemmas=len(set(lemma_ids)),
                num_whitespace_words=len(collection_whitespace_words[collection_id]),
                num_unique_whitespace_words=len(set(collection_whitespace_words[collection_id])),
            )
            for collection_id, lemma_ids in collection_lemma_ids.items()
        }

        actual_num_words, actual_lemmas = points[-1]
        all_xs = list(range(1, actual_num_words+1))
        print(f"Projected lemma count at current word count ({actual_num_words}): {round(heaps_law(actual_num_words))}")
        print(f"Actual lemma count: {actual_lemmas}")

        print("Collections:")
        for collection_id, summary in collection_summaries.items():
            print()
            print(f"Collection {Collection.objects.get(id=collection_id).title}:")
            print(f"{summary.num_annotated_words} words according to annotation.")
            print(f"{summary.num_whitespace_words} words according to whitespace.")
            print(f"{summary.num_unique_annotated_lemmas} unique lemmas according to annotation.")
            print(f"{summary.num_unique_whitespace_words} unique words according to whitespace.")

        print()
        print("Documents:")
        for title, summary in document_summaries.items():
            if summary.num_annotated_words == 0:
                continue

            print()
            print(f"Document {title}:")
            print(f"{summary.num_annotated_words} words according to annotation.")
            print(f"{summary.num_whitespace_words} words according to whitespace.")
            print(f"{summary.num_unique_annotated_lemmas} unique lemmas according to annotation.")
            print(f"{summary.num_unique_whitespace_words} unique words according to whitespace.")

        plt.plot(*zip(*points))
        plt.plot(all_xs, list(map(heaps_law, all_xs)))
        plt.show()
