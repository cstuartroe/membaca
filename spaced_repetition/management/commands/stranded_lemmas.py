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

                all_trials = []
                all_lemma_adds = []

                for lemma_add in LemmaAdd.objects.filter(lemma_id=lemma.id):
                    all_lemma_adds.append(lemma_add)

                    trials = list(Trial.objects.filter(lemma_add_id=lemma_add.id).order_by('time_created'))
                    all_trials += trials

                    if not trials:
                        print(f"{lemma_add.user.username} has never trialed this lemma")
                    else:
                        print(f"This lemma comes due for {lemma_add.user.username} "
                              f"on {trials[-1].due_date()} with trial type {TRIAL_TYPE_CYCLE[trials[-1].trial_type]}")

                print(f"Deleting this lemma will delete {len(all_trials)} trials and {len(all_lemma_adds)} lemma adds.")
                delete = input("Delete? ")
                if delete.lower().strip() == "y":
                    for trial in all_trials:
                        trial.delete()
                    for lemma_add in all_lemma_adds:
                        lemma_add.delete()
                    lemma.delete()

                print()

