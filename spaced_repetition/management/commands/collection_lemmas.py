import re
from dataclasses import dataclass
from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt
from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.document import Document
from spaced_repetition.models.language import LANGUAGE_IDS


class Command(BaseCommand):
    help = 'Shows the accumulation of new lemmas in each collection in a language'

    def add_arguments(self, parser):
        parser.add_argument("-l", "--language", required=True)

    def handle(self, *args, **options):
        collections_by_id = {}
        collection_lemma_progressions = {}
        collection_lemma_sets = {}

        for document in (
            Document.objects
            .select_related('collection')
            .filter(collection__language_id=LANGUAGE_IDS[options["language"]])
            .order_by('id')
            .prefetch_related('sentence_set')
            .prefetch_related('sentence_set__words_in_sentence')
        ):
            cid = document.collection_id

            if document.collection_id not in collections_by_id:
                collections_by_id[cid] = document.collection
                collection_lemma_progressions[cid] = [(0, 0)]
                collection_lemma_sets[cid] = set()

            sentences = list(document.sentence_set.all())
            sentences.sort(key=lambda s: s.position)

            for sentence in sentences:
                words = list(sentence.words_in_sentence.all())
                words.sort(key=lambda w: w.id)

                for word in words:
                    words, lemmas = collection_lemma_progressions[cid][-1]
                    if word.lemma_id not in collection_lemma_sets[cid]:
                        collection_lemma_sets[cid].add(word.lemma_id)
                        lemmas += 1
                    collection_lemma_progressions[cid].append((words + 1, lemmas))

        for collection_id, lemma_set in collection_lemma_sets.items():
            other_lemmas = set()
            for collection_id2, lemma_set2 in collection_lemma_sets.items():
                if collection_id2 == collection_id:
                    continue

                other_lemmas |= lemma_set2

            unique_lemmas = lemma_set - other_lemmas
            print(f"{collections_by_id[collection_id].title} has {len(unique_lemmas)} unique lemmas, including:")
            example_unique = Lemma.objects.filter(id__in=unique_lemmas).order_by("?")[:5]
            for lemma in example_unique:
                print(f"    {lemma.citation_form} \"{lemma.translation}\"")

        for collection_id, progression in collection_lemma_progressions.items():
            plt.plot(*zip(*progression), label=collections_by_id[collection_id].title)

        plt.legend()
        plt.show()
