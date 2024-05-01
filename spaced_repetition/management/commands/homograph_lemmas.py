import json
from django.core.management.base import BaseCommand
from spaced_repetition.models.language import LANGUAGE_IDS
from spaced_repetition.models.lemma import Lemma


class Command(BaseCommand):
    help = 'Finds all homographic lemmas'

    def add_arguments(self, parser):
        parser.add_argument("-l", "--language", required=True)

    def handle(self, *args, **options):
        lemmas_by_citation_form: dict[str, list[Lemma]] = {}
        for lemma in Lemma.objects.filter(language_id=LANGUAGE_IDS[options["language"]]).order_by("id"):
            if lemma.citation_form not in lemmas_by_citation_form:
                lemmas_by_citation_form[lemma.citation_form] = []
            lemmas_by_citation_form[lemma.citation_form].append(lemma)

        duplicate_citation_forms = [
            citation_form
            for citation_form, lemmas in lemmas_by_citation_form.items()
            if len(lemmas) > 1
        ]
        duplicate_citation_forms.sort(key=lambda f: max(lemma.id for lemma in lemmas_by_citation_form[f]))

        for form in duplicate_citation_forms:
            print(form)
            for lemma in lemmas_by_citation_form[form]:
                print(f"{lemma.id} {json.dumps(lemma.translation)}")
            print()
