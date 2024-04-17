from django.core.management.base import BaseCommand
from spaced_repetition.models.language import LANGUAGE_IDS
from spaced_repetition.models.lemma import Lemma


class Command(BaseCommand):
    help = 'Exports all tables into CSV files'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        dutch_id = LANGUAGE_IDS["Dutch"]

        gender_counts = {}
        for lemma in Lemma.objects.filter(language_id=dutch_id):
            gender = lemma.metadata_value("gender")
            gender_counts[gender] = gender_counts.get(gender, 0) + 1

        total = sum(gender_counts.values())

        for gender, count in gender_counts.items():
            print(gender, count, f"{round(100*count/total, 1)}%")
        