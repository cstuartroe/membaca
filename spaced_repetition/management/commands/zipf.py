import json
from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt
from spaced_repetition.models.language import LANGUAGE_IDS
from spaced_repetition.models.word_in_sentence import WordInSentence
from .lemmas_function import HEAPS_K, HEAPS_BETA, heaps_law


TOP_WORDS = 20
COVERAGE_LEVELS = [90, 95, 98, 99]


def predicted_corpus_size_for_coverage(coverage_percent: float):
    percent_of_corpus_that_is_hapax_legomena = 1 - coverage_percent/100
    return (2*percent_of_corpus_that_is_hapax_legomena/HEAPS_K)**(1/(HEAPS_BETA-1))


class Command(BaseCommand):
    help = 'Finds all homographic lemmas'

    def add_arguments(self, parser):
        parser.add_argument("-l", "--language", required=True)

    def handle(self, *args, **options):
        language_id = LANGUAGE_IDS[options["language"]]

        lemmas_counts = {}
        total_count = 0
        for word in WordInSentence.objects.select_related("lemma").all():
            if word.lemma is None:
                continue
            if word.lemma.language_id != language_id:
                continue

            if word.lemma.id not in lemmas_counts:
                lemmas_counts[word.lemma.id] = [word.lemma, 0]
            lemmas_counts[word.lemma.id][1] += 1
            total_count += 1

        lemmas_counts_list = list(lemmas_counts.values())
        lemmas_counts_list.sort(key=lambda t: t[1])

        print(f"Top {TOP_WORDS} lemmas:")
        for lemma, count in lemmas_counts_list[-TOP_WORDS:]:
            print(f"{count} ({count*100/total_count:.1f}%) {lemma.citation_form} {json.dumps(lemma.translation)}")
        print()

        print(f"{len(lemmas_counts_list)} total lemmas.")
        print(f"{total_count} total words.")

        coverage_i = 0
        cumulative_coverage = 0
        for i, (_, count) in enumerate(lemmas_counts_list[::-1]):
            cumulative_coverage += count
            if cumulative_coverage >= total_count*COVERAGE_LEVELS[coverage_i]/100:
                print(f"{COVERAGE_LEVELS[coverage_i]}% coverage: {i+1} lemmas")
                coverage_i += 1

                if coverage_i == len(COVERAGE_LEVELS):
                    break

        count_counts: dict[int, int] = {
            count: 0
            for count in range(1, lemmas_counts_list[-1][1] + 10)
        }
        for _, count in lemmas_counts_list:
            count_counts[count] += 1

        print(f"{count_counts[1]} hapax legomena.")

        hapax_legomena_percent = count_counts[1] / len(lemmas_counts_list)
        print(f"{round(100*hapax_legomena_percent)}% of lemmas are hapax legomena")

        coverage_without_hapax_legomena = (
            (total_count - count_counts[1])
            / total_count
        )
        print(f"{100*coverage_without_hapax_legomena:.1f}% coverage without hapax legomena")
        for percent in COVERAGE_LEVELS:
            print(
                f"Predicted number of total lemmas for {percent}% coverage without hapax legomena: "
                f"{round(heaps_law(predicted_corpus_size_for_coverage(percent)))}"
            )

        print({count: count_counts[count] for count in range(1, 21)})
        print()

        plt.plot(*zip(*sorted(list(count_counts.items()))), marker='o')
        plt.xscale('log')
        plt.yscale('log')
        plt.show()
