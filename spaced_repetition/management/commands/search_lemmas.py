from django.core.management.base import BaseCommand
from spaced_repetition.models.language import LANGUAGE_IDS
from spaced_repetition.views.search_lemmas import get_search_results


class Command(BaseCommand):
    help = 'Search for words based on a search string'

    def add_arguments(self, parser):
        parser.add_argument("-l", "--language", required=True)
        parser.add_argument("query")

    def handle(self, *args, **options):
        results = get_search_results(
            language_id=LANGUAGE_IDS[options["language"]],
            search_string=options["query"],
            num_results=10,
        )[0]

        for result in results:
            print(result.lemma.id, result.lemma.citation_form, repr(result.lemma.translation))
