import os
import json
from django.core.management.base import BaseCommand
from django.db.models.fields import AutoField, BigAutoField, CharField, IntegerField, DateField, DateTimeField, BooleanField, EmailField, TextField
from django.db.models.fields.related import ManyToManyField, ForeignKey, OneToOneRel
from django.db.models.fields.reverse_related import ManyToOneRel, ManyToManyRel

from spaced_repetition.models.collection import Collection
from spaced_repetition.models.document import Document
from spaced_repetition.models.language import Language
from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.lemma_add import LemmaAdd
from spaced_repetition.models.sentence import Sentence
from spaced_repetition.models.sentence_add import SentenceAdd
from spaced_repetition.models.trial import Trial
from spaced_repetition.models.user import User
from spaced_repetition.models.user_settings import UserSettings
from spaced_repetition.models.word_in_sentence import WordInSentence


MODELS_TO_TRANSPILE = [
    Collection,
    Document,
    Language,
    Lemma,
    LemmaAdd,
    Sentence,
    SentenceAdd,
    Trial,
    User,
    UserSettings,
    WordInSentence,
]


def csv_escape(e):
    if isinstance(e, str):
        return json.dumps(e)
    else:
        return str(e)


def csv_row(items):
    return ",".join(map(csv_escape, items)) + "\n"


class Command(BaseCommand):
    help = 'Transpiles Django models into a Typescript type definition file'

    def add_arguments(self, parser):
        parser.add_argument("destination", type=str, help="The directory into which to write backups")

    def handle(self, *args, **options):
        for model in MODELS_TO_TRANSPILE:
            header_row = []
            for field in model._meta.get_fields():
                t = type(field)

                if t in (AutoField, IntegerField, BooleanField, CharField, TextField, DateTimeField, EmailField):
                    header_row.append(field.name)
                elif t is ForeignKey:
                    header_row.append(f"{field.name}_id")
                elif t is ManyToManyField:
                    print(f"Skipping ManyToManyField field {field.name} of table {model._meta.db_table}")
                elif t is ManyToOneRel:
                    print(f"Skipping ManyToOneRel field {field.name} of table {model._meta.db_table}")
                elif t is OneToOneRel:
                    print(f"Skipping OneToOneRel field {field.name} of table {model._meta.db_table}")
                else:
                    raise ValueError(f"Unknown field type: {t}")

            rows = []
            for row in model.objects.order_by("id").all():
                rows.append([
                    getattr(row, field_name)
                    for field_name in header_row
                ])

            filepath = os.path.join(options["destination"], model._meta.db_table + ".csv")
            with open(filepath, "w") as fh:
                fh.write(csv_row(header_row))
                for row in rows:
                    fh.write(csv_row(row))
