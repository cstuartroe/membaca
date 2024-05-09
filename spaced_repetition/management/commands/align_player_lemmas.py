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
    help = 'Sets the LemmaAdds for one player equal to another.'

    def add_arguments(self, parser):
        parser.add_argument("-l", "--language", required=True)
        parser.add_argument("-s", "--source_user_id", required=True)
        parser.add_argument("-t", "--target_user_id", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        language_id = LANGUAGE_IDS[options["language"]]

        source_user_lemma_ids = {
            lemma_add.lemma_id: lemma_add
            for lemma_add in (
                LemmaAdd.objects.select_related('lemma')
                .filter(lemma__language_id=language_id)
                .filter(user_id=options["source_user_id"])
            )
        }
        target_user_lemma_adds = {
            lemma_add.lemma_id: lemma_add
            for lemma_add in (
                LemmaAdd.objects.select_related('lemma')
                .filter(lemma__language_id=language_id)
                .filter(user_id=options["target_user_id"])
            )
        }

        to_delete = [
            lemma_add
            for lemma_add in target_user_lemma_adds.values()
            if lemma_add.lemma_id not in source_user_lemma_ids
        ]
        to_create = [
            lemma_add.lemma
            for lemma_add in source_user_lemma_ids.values()
            if lemma_add.lemma_id not in target_user_lemma_adds
        ]

        to_delete.sort(key=lambda lemma_add: lemma_add.lemma.id)
        to_create.sort(key=lambda lemma: lemma.id)

        if to_delete:
            print(f"{len(to_delete)} lemma adds to delete:")
            for lemma_add in to_delete:
                print(f"{lemma_add.lemma.citation_form} {json.dumps(lemma_add.lemma.translation)}")
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
                            user_id=options["target_user_id"],
                            time_created=creation_time,
                        ).save()

                if to_delete:
                    print("Deleting...")
                    for lemma_add in tqdm(to_delete):
                        for metadata_trial in MetadataTrial.objects.filter(lemma_add=lemma_add):
                            metadata_trial.delete()
                        for trial in Trial.objects.filter(lemma_add=lemma_add):
                            trial.delete()

                        lemma_add.delete()
