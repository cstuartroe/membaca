import argparse
from django.core.management.base import BaseCommand
from spaced_repetition.models.sentence import Sentence
from spaced_repetition.models.language import LANGUAGE_IDS
from spaced_repetition.models.metadata_trial import MetadataTrial
from spaced_repetition.models.trial import Trial


class Command(BaseCommand):
    help = 'Find the most-trialed lemmas and sentences'

    def add_arguments(self, parser):
        parser.add_argument("-l", "--language", required=True)
        parser.add_argument("-u", "--user_id", required=True)
        parser.add_argument('-w', '--wrong', type=bool, action=argparse.BooleanOptionalAction)
        parser.add_argument('-m', '--metadata', type=bool, action=argparse.BooleanOptionalAction)

    def handle(self, *args, **options):
        lemma_counts = {}
        sentence_counts = {}

        if options["metadata"]:
            klass = MetadataTrial
        else:
            klass = Trial

        for trial in (
                klass.objects
                .select_related("lemma_add")
                .select_related("lemma_add__lemma")
                .filter(
                    lemma_add__lemma__language_id=LANGUAGE_IDS[options["language"]],
                    lemma_add__user_id=options["user_id"],
                )
        ):
            if options['wrong'] and trial.correct:
                continue

            lemma_counts[trial.lemma_add.lemma] = lemma_counts.get(trial.lemma_add.lemma, 0) + 1

            if not options["metadata"] and trial.sentence_id is not None:
                sentence_counts[trial.sentence_id] = sentence_counts.get(trial.sentence_id, 0) + 1

        for lemma, count in sorted(list(lemma_counts.items()), key=lambda x: x[1])[-100:]:
            print(count, lemma)

        print()
        print()

        for sentence_id, count in sorted(list(sentence_counts.items()), key=lambda x: x[1])[-20:]:
            print(count, Sentence.objects.get(id=sentence_id))
            print()
