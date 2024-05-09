import json
from django.core.management.base import BaseCommand
from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.lemma_add import LemmaAdd
from spaced_repetition.models.trial import Trial
from spaced_repetition.models.word_in_sentence import WordInSentence
from spaced_repetition.views.cards import TRIAL_TYPE_CYCLE


class Command(BaseCommand):
    help = 'Finds all stranded lemmas'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        lemma_ids = set()
        for word in WordInSentence.objects.all():
            lemma_ids.add(word.lemma_id)

        for lemma in Lemma.objects.all():
            if lemma.id not in lemma_ids:
                print(f"{lemma.language.name} lemma {lemma.citation_form} {json.dumps(lemma.translation)}")

                for lemma_add in LemmaAdd.objects.filter(lemma_id=lemma.id):
                    trials = list(Trial.objects.filter(lemma_add_id=lemma_add.id).order_by('time_created'))

                    if not trials:
                        print(f"{lemma_add.user.username} has never trialed this lemma")
                    else:
                        print(f"This lemma comes due for {lemma_add.user.username} "
                              f"on {trials[-1].due_date()} with trial type {TRIAL_TYPE_CYCLE[trials[-1].trial_type]}")

