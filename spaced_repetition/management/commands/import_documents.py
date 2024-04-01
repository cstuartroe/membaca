import argparse
import html
import os
import re

from bs4 import BeautifulSoup as bs
from django.core.management.base import BaseCommand
from django.db import transaction
from google.cloud import translate
from tqdm import tqdm

from spaced_repetition.models.document import Document
from spaced_repetition.models.sentence import Sentence

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

    return html.unescape(response.translations[0].translated_text)


CHARACTER_REPLACEMENTS = {
    "‘": "'",
    "’": "'",
    "…": "...",
    "–": "-",
}


@transaction.atomic
def parse_tom_poes(content: str, options: dict):
    num_documents = Document.objects.filter(collection_id=options["collection_id"]).count()

    document = Document(
        title=options["title"],
        collection_id=options["collection_id"],
        order=num_documents,
        link="foobar",
    )
    document.save()

    sentence_index = 0

    matches = re.findall("<body.*?</body>", content, flags=re.DOTALL)
    for match in tqdm(matches):
        soup = bs(match, features="html.parser")
        image_link = soup.find("img", {"class": "strook"})["src"]
        image_filename = image_link.split("/")[-1]
        new_image_address = options["object_storage_address"] + image_filename

        for i, p in enumerate(soup.find_all("p")):
            text = re.sub(r"\s+", " ", p.text.strip())
            for character, replacement in CHARACTER_REPLACEMENTS.items():
                text = text.replace(character, replacement)

            if i == 0:
                image = new_image_address
            else:
                image = ""

            sentence = Sentence(
                document_id=document.id,
                position=sentence_index,
                text=text,
                translation=translate_text(text, "nl", "en"),
                image=image,
            )
            sentence.save()
            sentence_index += 1


PARSING_DISPATCH_TABLE = {
    "tom_poes": parse_tom_poes,
}


class Command(BaseCommand):
    help = 'Indexes the words'

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("source_file", type=str)
        parser.add_argument('-T', '--title', type=str, required=True)
        parser.add_argument('-t', '--type', type=str, choices=list(PARSING_DISPATCH_TABLE.keys()))
        parser.add_argument('-c', '--collection_id', type=int, required=False)
        parser.add_argument('-o', '--object_storage_address', type=str, required=False)

    def handle(self, *args, **options):
        with open(options["source_file"], "r") as fh:
            content = fh.read()

        PARSING_DISPATCH_TABLE[options["type"]](content, options)
