import json
from django.core.management.base import BaseCommand
from django.db import transaction
from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.lemma_add import LemmaAdd
from spaced_repetition.models.metadata_trial import MetadataTrial
from spaced_repetition.models.trial import Trial
from spaced_repetition.models.word_in_sentence import WordInSentence
from spaced_repetition.models.user import User


@transaction.atomic
def merge_lemmas(keep_id: int, merge_id: int):
    # just make sure they both exist
    lemma_to_keep = Lemma.objects.get(id=keep_id)
    lemma_to_merge = Lemma.objects.get(id=merge_id)

    for word in WordInSentence.objects.filter(lemma_id=merge_id):
        word.lemma_id = keep_id
        word.save()

    for user in User.objects.all():
        keep_lemma_add = LemmaAdd.objects.filter(lemma_id=keep_id, user_id=user.id).first()
        merge_lemma_add = LemmaAdd.objects.filter(lemma_id=merge_id, user_id=user.id).first()

        if merge_lemma_add:
            if keep_lemma_add:
                for trial in Trial.objects.filter(lemma_add_id=merge_lemma_add.id):
                    trial.lemma_add_id = keep_lemma_add.id
                    trial.save()
                for trial in MetadataTrial.objects.filter(lemma_add_id=merge_lemma_add.id):
                    trial.lemma_add_id = keep_lemma_add.id
                    trial.save()
                merge_lemma_add.delete()
            else:
                merge_lemma_add.lemma_id = keep_id
                merge_lemma_add.save()

    lemma_to_merge.delete()


class Command(BaseCommand):
    help = 'Merges mistakenly created duplicate lemmas'

    def add_arguments(self, parser):
        parser.add_argument("keep", type=int)
        parser.add_argument("merge", type=int)

    def handle(self, *args, **options):
        merge_lemmas(options["keep"], options["merge"])

