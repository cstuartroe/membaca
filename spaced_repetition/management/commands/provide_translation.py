from tqdm import tqdm
from django.core.management.base import BaseCommand
from django.db import transaction
from .import_documents import translate_text
from spaced_repetition.models.sentence import Sentence


LANGUAGE_CODES = {
    "Dutch": "nl",
}


class Command(BaseCommand):
    help = 'Google translates all sentences'

    def add_arguments(self, parser):
        parser.add_argument("-l", "--language", required=True)
        parser.add_argument("-d", "--document_id", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        language_code = LANGUAGE_CODES[options["language"]]

        sentences = list(Sentence.objects.filter(document_id=options["document_id"]))
        for sentence in tqdm(sentences):
            sentence.translation = translate_text(sentence.text, language_code, "en")
            sentence.save()
