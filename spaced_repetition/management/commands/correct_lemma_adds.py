import datetime
import json

from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from spaced_repetition.models.language import LANGUAGE_IDS
from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.lemma_add import LemmaAdd
from spaced_repetition.models.metadata_trial import MetadataTrial
from spaced_repetition.models.sentence_add import SentenceAdd
from spaced_repetition.models.trial import Trial


class Command(BaseCommand):
    help = (
        'Prunes lemma adds for lemmas which a user has only read '
        'once, and creates ones for lemmas they\'ve read more '
        'than once.'
    )

    def add_arguments(self, parser):
        parser.add_argument("-l", "--language", required=True)
        parser.add_argument("-u", "--user_id", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        language_id = LANGUAGE_IDS[options["language"]]

        times_seen_per_lemma = {}

        print("Counting times lemmas seen...")
        for sentence_add in (
            SentenceAdd.objects.filter(user_id=options["user_id"])
            .select_related('sentence')
            .select_related('sentence__document')
            .select_related('sentence__document__collection')
            .filter(sentence__document__collection__language_id=language_id)
            .prefetch_related('sentence__words_in_sentence')
        ):
            for word in sentence_add.sentence.words_in_sentence.all():
                if word.lemma_id is None:
                    continue

                times_seen_per_lemma[word.lemma_id] = times_seen_per_lemma.get(word.lemma_id, 0) + 1

        lemmas_by_id = {
            lemma.id: lemma
            for lemma in Lemma.objects.filter(language_id=language_id)
        }
        lemma_adds_by_lemma_id = {}
        for lemma_add in LemmaAdd.objects.filter(user_id=options["user_id"]):
            if lemma_add.lemma_id in lemma_adds_by_lemma_id:
                raise ValueError

            lemma_adds_by_lemma_id[lemma_add.lemma_id] = lemma_add

        to_delete = []
        to_create = []
        print("Calculating lists to create and delete...")
        for lemma_id, times in times_seen_per_lemma.items():
            lemma_add_exists = lemma_id in lemma_adds_by_lemma_id

            if times < 2 and lemma_add_exists:
                to_delete.append(lemmas_by_id[lemma_id])
            elif times >= 2 and not lemma_add_exists:
                to_create.append(lemmas_by_id[lemma_id])

        to_delete.sort(key=lambda lemma: lemma.id)
        to_create.sort(key=lambda lemma: lemma.id)

        if to_delete:
            print(f"{len(to_delete)} lemma adds to delete:")
            for lemma in to_delete:
                print(f"{lemma.citation_form} {json.dumps(lemma.translation)}")
        else:
            print("No lemma adds to delete.")
        print()
        if to_create:
            print(f"{len(to_create)} lemma adds to create:")
            for lemma in to_create:
                print(f"{lemma.citation_form} {json.dumps(lemma.translation)}")
        else:
            print("No lemma adds to create.")
        print()

        if to_delete or to_create:
            do_it = input("Proceeed? ")

            if do_it.lower().strip() == "y":
                creation_time = datetime.datetime.utcnow()

                if to_create:
                    print("Creating...")
                    for lemma in tqdm(to_create):
                        LemmaAdd(
                            lemma_id=lemma.id,
                            user_id=options["user_id"],
                            time_created=creation_time,
                        ).save()

                if to_delete:
                    print("Deleting...")
                    for lemma in tqdm(to_delete):
                        lemma_add = lemma_adds_by_lemma_id[lemma.id]

                        for metadata_trial in MetadataTrial.objects.filter(lemma_add=lemma_add):
                            metadata_trial.delete()
                        for trial in Trial.objects.filter(lemma_add=lemma_add):
                            trial.delete()

                        lemma_add.delete()
