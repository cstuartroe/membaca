from dataclasses import dataclass

from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt

from spaced_repetition.models.language import LANGUAGE_IDS
from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.word import Word


@dataclass
class LemmaVariantInfo:
    lemma: Lemma
    variants: set[str]


class Command(BaseCommand):
    help = 'Gets number of variants for lemmas'

    def add_arguments(self, parser):
        parser.add_argument("-l", "--language", required=True)

    def handle(self, *args, **options):
        language_id = LANGUAGE_IDS[options["language"]]

        lemma_variants_by_id: dict[int, LemmaVariantInfo] = {}

        for word in Word.objects.select_related('lemma').filter(language_id=language_id):
            if word.lemma_id not in lemma_variants_by_id:
                lemma_variants_by_id[word.lemma_id] = LemmaVariantInfo(
                    lemma=word.lemma,
                    variants=set(),
                )

            lemma_variants_by_id[word.lemma_id].variants.add(word.word)

        lemma_variants = list(lemma_variants_by_id.values())
        lemma_variants.sort(key=lambda v: len(v.variants), reverse=True)

        for info in lemma_variants[:5]:
            print(info.lemma.citation_form, repr(info.lemma.translation))
            print(", ".join(info.variants))

        variant_counts = {}
        for info in lemma_variants:
            num_variants = len(info.variants)
            variant_counts[num_variants] = variant_counts.get(num_variants, 0) + 1

        variant_counts = [
            (count, variant_counts.get(count, 0))
            for count in range(1, len(lemma_variants[0].variants) + 1)
        ]

        print(variant_counts)

        plt.plot(*zip(*variant_counts), marker='o')
        plt.yscale('log')
        plt.show()
