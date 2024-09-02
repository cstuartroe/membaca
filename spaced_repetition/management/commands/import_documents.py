import argparse
import html
import os
import re

from bs4 import BeautifulSoup as bs
from django.core.management.base import BaseCommand
from django.db import transaction
from google.cloud import translate
from tqdm import tqdm

from spaced_repetition.models.collection import Collection
from spaced_repetition.models.document import Document
from spaced_repetition.models.language import LANGUAGE_IDS
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
    "“": "\"",
    "”": "\"",
    "′": "'",
}


def sanitize_text(text):
    text = re.sub(r"\s+", " ", text.strip())
    for character, replacement in CHARACTER_REPLACEMENTS.items():
        text = text.replace(character, replacement)
    return text


def parse_tom_poes(content: str, document_id: int, object_storage_address: str | None):
    sentence_index = 0

    matches = re.findall("<body.*?</body>", content, flags=re.DOTALL)
    for match in tqdm(matches):
        soup = bs(match, features="html.parser")
        image_link = soup.find("img", {"class": "strook"})["src"]
        image_filename = image_link.split("/")[-1]
        new_image_address = object_storage_address + image_filename

        for i, p in enumerate(soup.find_all("p")):
            text = sanitize_text(p.text)

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
    image = ""
    for child in clearfix.children:
        if child.name and child.find("div", {"class": "photo"}):
            image = child.find("div", {"class": "photo"}).img.attrs["src"]

        if child.name == "p":
            if child.text.startswith("Baca juga:"):
                continue

            format_level = Sentence.FormatLevel.NEW_SECTION if sentence_index == 2 else Sentence.FormatLevel.P
        elif child.name == "h3":
            format_level = Sentence.FormatLevel.H3
        elif child.name == "h2":
            format_level = Sentence.FormatLevel.H2
        else:
            continue

        if child.text == "":
            continue

        Sentence(
            document_id=document_id,
            position=sentence_index,
            text=child.text,
            translation=translate_text(child.text, "id", "en"),
            format_level=format_level,
            image=image,
        ).save()
        sentence_index += 1
        image = ""


def parse_ontdekking(content: str, object_storage_address: str):
    LINK = "https://www.onlinebibliotheek.nl/catalogus/370837061/de-ontdekking-van-de-hemel-harry-mulisch"

    html_children = []

    matches = re.findall("<html.*?</html>", content, flags=re.DOTALL)
    for match in matches:
        soup = bs(match, features="html.parser")
        html_children += [child for child in soup.body.div.div.children if child.name is not None]

    chapters = []

    for i, child in enumerate(html_children):
        text = child.text.strip().replace("  ", " ").replace("–", "-")
        if text == "":
            continue

        if child.name == "p":
            if chapters:
                chapters[-1][1].append(text)

        elif child.name == "h1":
            if chapters:
                del chapters[-1][1][-1]

        elif child.name == "h2":
            chapters.append((text, []))

        else:
            raise ValueError(f"Unknown child name: {child.name}")

    collection = Collection(
        title="De ontdekking van hemel",
        language_id=LANGUAGE_IDS["Dutch"],
    )
    collection.save()

    for i, chapter in tqdm(list(enumerate(chapters))):
        title, sentences = chapter

        document = Document(
            title=title,
            collection=collection,
            order=i+1,
            link=LINK,
        )
        document.save()

        for i, sentence_text in enumerate(sentences):
            sentence = Sentence(
                document=document,
                position=i+1,
                text=sentence_text,
                translation="",
            )
            sentence.save()


def hallo_witte_mensen(content: str, object_storage_address: str):
    collection = Collection(
        title="Hallo Witte Mensen",
        language_id=LANGUAGE_IDS["Dutch"],
    )
    collection.save()

    matches = re.findall("<html.*?</html>", content, flags=re.DOTALL)
    for i, match in enumerate(tqdm(matches)):
        soup = bs(match, features="html.parser")
        text_frame = soup.body.find("div", {"class": "Basic-Text-Frame"})

        sentence_index = 1
        document = None

        for child in text_frame.children:
            if child.name is None:
                continue

            assert child.name in ("p", "table")

            text = sanitize_text(child.text)

            if text == "Aanbevolen om te lezen en te kijken":
                break

            if child["class"] == ["AUP_T1_W"]:
                document = Document(
                    title=text,
                    collection=collection,
                    order=i+1,
                    link="https://www.onlinebibliotheek.nl/catalogus/409838934/hallo-witte-mensen-anousha-nzume",
                )
                document.save()

                Sentence(
                    document=document,
                    position=sentence_index,
                    text=text,
                    translation="",
                    format_level=Sentence.FormatLevel.H1,
                ).save()

                sentence_index += 1
            elif child["class"] in (["AUP_T2_NoNumber_ZW"], ["AUP_T2_NoNumber"]):
                Sentence(
                    document=document,
                    position=sentence_index,
                    text=text,
                    translation="",
                    format_level=Sentence.FormatLevel.H2,
                ).save()

                sentence_index += 1
            elif child.name == "table":
                for row in child.find_all("tr"):
                    texts = []
                    for col in row.find_all("td"):
                        texts.append(col.text)
                    text = sanitize_text(" - ".join(texts))

                    Sentence(
                        document=document,
                        position=sentence_index,
                        text=text,
                        translation="",
                        format_level=Sentence.FormatLevel.P,
                    ).save()

                    sentence_index += 1

            else:
                Sentence(
                    document=document,
                    position=sentence_index,
                    text=text,
                    translation="",
                    format_level=Sentence.FormatLevel.P,
                ).save()

                sentence_index += 1


def parse_natgeo(content: str, object_storage_address: str, document_id: int):
    """HTML escaped inside HTML. The goriest thing I've ever seen."""

    onion_soup = bs(content, features="html.parser")
    # second_layer = ""
    # for span in onion_soup.find("td", {"class": "line-content"}).children:
    #     second_layer += span.text + "\n"

    second_soup = onion_soup # bs(second_layer, features="html.parser")

    title = second_soup.find("h1", {"class": "css-1o0b1xw"}).text.strip()
    subtitle = second_soup.find("div", {"class": "css-19lo7rm"}).text.strip()
    image_addr = second_soup.find("picture", {"class": "css-1oxikel"}).img.attrs["src"]

    Sentence(
        document_id=document_id,
        position=1,
        text=title,
        translation=translate_text(title, "nl", "en"),
        format_level=Sentence.FormatLevel.H2,
    ).save()
    Sentence(
        document_id=document_id,
        position=2,
        text=subtitle,
        translation=translate_text(subtitle, "nl", "en"),
        format_level=Sentence.FormatLevel.P,
        image=image_addr,
    ).save()

    position = 3
    for child in second_soup.find("div", {"class": "article-body-content"}).children:
        if child.name in ["p", "h2"]:
            text = child.text.strip().replace("\n", "")

            if text.startswith("Nog niet uitgelezen?"):
                break

            if child.name == "h2":
                format_level = Sentence.FormatLevel.H3
            elif position == 3:
                format_level = Sentence.FormatLevel.NEW_SECTION
            else:
                format_level = Sentence.FormatLevel.P

            text = sanitize_text(text)

            Sentence(
                document_id=document_id,
                position=position,
                text=text,
                translation=translate_text(text, "nl", "en"),
                format_level=format_level,
            ).save()
            position += 1



PARSING_DISPATCH_TABLE = {
    "tom_poes": parse_tom_poes,
    "kompas": parse_kompas,
    "de_ontdekking_van_hemel": parse_ontdekking,
    "hallo_witte_mensen": hallo_witte_mensen,
    "natgeo": parse_natgeo,
}


class Command(BaseCommand):
    help = 'Indexes the words'

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("source_file", type=str)
        parser.add_argument('-T', '--title', type=str, required=False)
        parser.add_argument('-t', '--type', type=str, choices=list(PARSING_DISPATCH_TABLE.keys()))
        parser.add_argument('-c', '--collection_id', type=int, required=False)
        parser.add_argument('-o', '--object_storage_address', type=str, required=False)

    @transaction.atomic
    def handle(self, *args, **options):
        with open(options["source_file"], "r") as fh:
            content = fh.read()

        def parse(**kwargs):
            parse_function = PARSING_DISPATCH_TABLE[options["type"]]

            parse_function(
                content,
                object_storage_address=options["object_storage_address"],
                **kwargs
            )

        if options["collection_id"] is None:
            parse()
            return

        num_documents = Document.objects.filter(collection_id=options["collection_id"]).count()

        document = Document(
            title=options["title"],
            collection_id=options["collection_id"],
            order=num_documents,
            link="foobar",
        )
        document.save()

        parse(document_id=document.id)
