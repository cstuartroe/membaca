from django.core.management.base import BaseCommand
from django.db import transaction
from spaced_repetition.models.document import Document
from spaced_repetition.models.sentence import Sentence


REPLACEMENTS = {
    "‘": "'",
    "’": "'",
    "“": "\"",
    "”": "\"",
}


class Command(BaseCommand):
    help = 'Replaces unwanted unicode characters'

    def add_arguments(self, parser):
        parser.add_argument("-c", "--collection_id", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        for document in Document.objects.filter(collection_id=options["collection_id"]):
            for sentence in Sentence.objects.filter(document_id=document.id):
                for key, value in REPLACEMENTS.items():
                    assert len(key) == len(value)
                    sentence.text = sentence.text.replace(key, value)

                sentence.text = sentence.text.strip()

                sentence.save()
