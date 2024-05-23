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


def parse_tom_poes(content: str, document_id: int, object_storage_address: str | None):
    sentence_index = 0

    matches = re.findall("<body.*?</body>", content, flags=re.DOTALL)
    for match in tqdm(matches):
        soup = bs(match, features="html.parser")
        image_link = soup.find("img", {"class": "strook"})["src"]
        image_filename = image_link.split("/")[-1]
        new_image_address = object_storage_address + image_filename

        for i, p in enumerate(soup.find_all("p")):
            text = re.sub(r"\s+", " ", p.text.strip())
            for character, replacement in CHARACTER_REPLACEMENTS.items():
                text = text.replace(character, replacement)

            if i == 0:
                image = new_image_address
            else:
                image = ""

            sentence = Sentence(
                document_id=document_id,
                position=sentence_index,
                text=text,
                translation=translate_text(text, "nl", "en"),
                image=image,
            )
            sentence.save()
            sentence_index += 1


def parse_kompas(content: str, document_id: int, object_storage_address: str):
    soup = bs(content, features="html.parser")

    title = soup.find("h1", {"class": "read__title"}).text
    Sentence(
        document_id=document_id,
        position=0,
        text=title,
        translation=translate_text(title, "id", "en"),
        format_level=Sentence.FormatLevel.H2,
    ).save()

    photo_address = soup.find("div", {"class": "photo__wrap"}).img["src"]
    photo_caption = soup.find("div", {"class": "photo__caption"}).text
    Sentence(
        document_id=document_id,
        position=1,
        text=photo_caption,
        translation=translate_text(photo_caption, "id", "en"),
        format_level=Sentence.FormatLevel.P,
        image=photo_address,
    ).save()

    sentence_index = 2
    clearfix = soup.find("div", {"class": "read__content"}).div
    for child in clearfix.children:
        if child.name == "p":
            if child.text.startswith("Baca juga:"):
                continue

            format_level = Sentence.FormatLevel.NEW_SECTION if sentence_index == 2 else Sentence.FormatLevel.P
        elif child.name == "h3":
            format_level = Sentence.FormatLevel.H3
        else:
            continue

        Sentence(
            document_id=document_id,
            position=sentence_index,
            text=child.text,
            translation=translate_text(child.text, "id", "en"),
            format_level=format_level,
        ).save()
        sentence_index += 1


PARSING_DISPATCH_TABLE = {
    "tom_poes": parse_tom_poes,
    "kompas": parse_kompas,
}


class Command(BaseCommand):
    help = 'Indexes the words'

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("source_file", type=str)
        parser.add_argument('-T', '--title', type=str, required=True)
        parser.add_argument('-t', '--type', type=str, choices=list(PARSING_DISPATCH_TABLE.keys()))
        parser.add_argument('-c', '--collection_id', type=int, required=False)
        parser.add_argument('-o', '--object_storage_address', type=str, required=False)

    @transaction.atomic
    def handle(self, *args, **options):
        with open(options["source_file"], "r") as fh:
            content = fh.read()

        num_documents = Document.objects.filter(collection_id=options["collection_id"]).count()

        document = Document(
            title=options["title"],
            collection_id=options["collection_id"],
            order=num_documents,
            link="foobar",
        )
        document.save()

        parse_function = PARSING_DISPATCH_TABLE[options["type"]]

        parse_function(
            content,
            document.id,
            object_storage_address=options["object_storage_address"],
        )
