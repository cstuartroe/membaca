from django.core.management.base import BaseCommand
from django.db import transaction
from spaced_repetition.models.document import Document
from spaced_repetition.models.sentence import Sentence
from .import_documents import CHARACTER_REPLACEMENTS


class Command(BaseCommand):
    help = 'Replaces unwanted unicode characters'

    def add_arguments(self, parser):
        parser.add_argument("-c", "--collection_id", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        num_replacements = {}

        for document in Document.objects.filter(collection_id=options["collection_id"]):
            for sentence in Sentence.objects.filter(document_id=document.id):
                for key, value in CHARACTER_REPLACEMENTS.items():
                    if key in sentence.text:
                        num_replacements[key] = num_replacements.get(key, 0) + sentence.text.count(key)
                        sentence.text = sentence.text.replace(key, value)

                sentence.text = sentence.text.strip()

                sentence.save()

        for key, value in num_replacements.items():
            print(f"Replaced {key} {value} times.")
