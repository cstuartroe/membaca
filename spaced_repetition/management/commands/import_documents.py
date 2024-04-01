import os
from google.cloud import translate
from django.core.management.base import BaseCommand

GCLOUD_PROJECT_ID = os.getenv("GCLOUD_PROJECT_ID")
PARENT = f"projects/{GCLOUD_PROJECT_ID}"


def translate_text(text: str, source_language_code: str, target_language_code: str) -> str:
    client = translate.TranslationServiceClient()

    response = client.translate_text(
        parent=PARENT,
        contents=[text],
        source_language_code=source_language_code,
        target_language_code=target_language_code,
    )

    return response.translations[0].translated_text


class Command(BaseCommand):
    help = 'Indexes the words'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print(translate_text(
            text=(
                "Lake Tahoe is een groot zoetwatermeer in de "
                "Sierra Nevada, op de grens tussen de Amerikaanse "
                "staten Californië en Nevada. Het is het grootste "
                "bergmeer en op een na diepste meer van de Verenigde "
                "Staten. Het diepblauwe meer is een trekpleister "
                "voor binnenlands toerisme."
            ),
            source_language_code="nl",
            target_language_code="en",
        ))
