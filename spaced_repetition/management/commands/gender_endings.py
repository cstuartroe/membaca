from django.core.management.base import BaseCommand
from spaced_repetition.models.language import LANGUAGE_IDS
from spaced_repetition.models.lemma import Lemma, DutchGenderEvaluator


MAX_ENDING_LENGTH = 4
ENDING_PREVALENCE_THRESHOLD = 5


GENDER_ABBREVIATIONS = {
    "de": "c",     # comuun
    "het": "o",    # onzijdig
    "de/het": "x",
}


ENDINGS = [
    "schap",

    "heid",
    "teit",
    "ment",
    "ling",
    "icht",
    "acht",
    "tuur",
    "isme",

    "ing",
    "aal",
    "aar",
    "nis",
    "uur",
    "eur",
    "sel",
    "eel",
    "ist",

    "ie",
    "er",
    "el",
    "te",
    "de",
    "st",
    "en",
    "us",
    "um",
    "je",

    "e",
]


class Command(BaseCommand):
    help = 'Exports all tables into CSV files'

    def add_arguments(self, parser):
        parser.add_argument("-e", "--ending", default=None)

    def handle(self, *args, **options):
        dutch_id = LANGUAGE_IDS["Dutch"]
        lemmas = [
            lemma
            for lemma in Lemma.objects.filter(language_id=dutch_id)
            if (DutchGenderEvaluator.playable(lemma.metadata_value("gender")))
        ]
        lemmas_by_prevalent_ending = []

        carryover_lemmas = []
        for lemma in lemmas:
            ending_found = False
            for ending in ENDINGS:
                if lemma.citation_form.endswith(ending):
                    lemmas_by_prevalent_ending.append((lemma, ending))
                    ending_found = True
                    break

            if not ending_found:
                carryover_lemmas.append(lemma)
        lemmas = carryover_lemmas

        for i in range(MAX_ENDING_LENGTH, 0, -1):
            ending_counts = {}

            for lemma in lemmas:
                ending = lemma.citation_form[-i:]
                ending_counts[ending] = ending_counts.get(ending, 0) + 1

            carryover_lemmas = []
            for lemma in lemmas:
                ending = lemma.citation_form[-i:]
                if ending_counts[ending] >= ENDING_PREVALENCE_THRESHOLD:
                    lemmas_by_prevalent_ending.append((lemma, ending))
                else:
                    carryover_lemmas.append(lemma)

            lemmas = carryover_lemmas

        if options["ending"]:
            lemmas_to_show = [
                lemma
                for lemma, ending in lemmas_by_prevalent_ending
                if ending == options["ending"]
            ]
            lemmas_to_show.sort(key=lambda lemma: GENDER_ABBREVIATIONS[lemma.metadata_value("gender")])

            for lemma in lemmas_to_show:
                print(f"{lemma.metadata_value("gender"):<6} {lemma.citation_form}")

        else:
            for lemma in lemmas:
                print(f"{lemma.citation_form} has an uncommon ending")
            print()

            prevalent_ending_genders = {}
            for lemma, ending in lemmas_by_prevalent_ending:
                if ending not in prevalent_ending_genders:
                    prevalent_ending_genders[ending] = []

                prevalent_ending_genders[ending].append(GENDER_ABBREVIATIONS[lemma.metadata_value("gender")])

            for ending, genders in sorted(
                    list(prevalent_ending_genders.items()),
                    key=lambda x: (
                        max(
                            sum(1 if c == g else 0 for c in x[1])/len(x[1])
                            for g in GENDER_ABBREVIATIONS.values()
                        ),
                        len(x[1]),
                    )
            ):
                print(f"{ending:<5} {''.join(sorted(genders)):>4}")