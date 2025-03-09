import argparse
import html
import os
import re
from dataclasses import dataclass

from bs4 import BeautifulSoup as bs
from django.core.management.base import BaseCommand
from django.db import transaction
from google.cloud import translate
import requests
from tqdm import tqdm

from spaced_repetition.models.collection import Collection
from spaced_repetition.models.document import Document
from spaced_repetition.models.language import LANGUAGE_IDS
from spaced_repetition.models.sentence import Sentence


COLLECTIONS = [
    # Title               id  num pages
    ("Vere aŭ Fantazie", 106, 46),
    # ("La tuta Esperanto", 25, 23),
]


class Command(BaseCommand):
    help = 'Downloads content from lernu.net'

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    @transaction.atomic
    def handle(self, *args, **options):
        for title, lernu_id, num_pages in COLLECTIONS:
            collection = Collection(
                title=title,
                language_id=LANGUAGE_IDS["Esperanto"],
            )
            collection.save()

            for i in tqdm(list(range(num_pages))):
                page_num = i + 1
                url = f"https://lernu.net/biblioteko/{lernu_id}"
                if page_num > 1:
                    url += f"/{page_num}"

                res = requests.get(
                    url,
                    headers={
                        "Cookie": "YII_CSRF_TOKEN=WjRvZTZkYndCaGVDZTVxM1UwdERTWjVLdWVBQm5aYTUVXMAuyoIEj9ivcsfMvsPJWuOhbHDqnY9n_T84FW8nzg%3D%3D; 6f3c685240a5e5708fec4cb5df7baffe=582cfe3b9b4f861b856532f2af550e9333f4d91fa%3A4%3A%7Bi%3A0%3Bi%3A340361%3Bi%3A1%3Bs%3A10%3A%22cstuartroe%22%3Bi%3A2%3Bi%3A2592000%3Bi%3A3%3Ba%3A0%3A%7B%7D%7D; PHPSESSID=5eatp7uj1pmmft6r22k5ef31br; lang=en",
                    }
                )
                if res.status_code != 200:
                    raise RuntimeError

                directory = f"../membaca-content/documents/{title.lower().replace(' ', '_').replace('ŭ', 'ux')}"
                os.makedirs(directory, exist_ok=True)
                with open(os.path.join(directory, f"{page_num:03d}.html"), "wb") as fh:
                    fh.write(res.content)

                soup = bs(res.content, features="html.parser")
                content_div = soup.find("div", {"class": "media-text content-item"})
                page_title = content_div.find("h2").text.strip()
                document = Document(
                    title=page_title,
                    collection=collection,
                    order=page_num,
                    link=url,
                )
                document.save()
                for i, span in enumerate(content_div.find_all("span")):
                    sentence = Sentence(
                        document=document,
                        position=i + 1,
                        text=span.text.strip(),
                        translation="",
                        image="",
                        format_level=Sentence.FormatLevel.P,
                    )
                    sentence.save()
