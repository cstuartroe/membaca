from django.views import View
from django.http import HttpRequest, JsonResponse
from .ajax_utils import admin_only
from spaced_repetition.models.language import LANGUAGE_IDS
from spaced_repetition.models.lemma import Lemma


DUTCH_LANGUAGE_ID = LANGUAGE_IDS["Dutch"]


class DutchGenderlessWordsView(View):
    @admin_only
    def get(self, _request: HttpRequest):
        lemmas = Lemma.objects.filter(language_id=DUTCH_LANGUAGE_ID).order_by("id")

        lemmas_with_unspecified_gender = [
            lemma
            for lemma in lemmas
            if lemma.metadata_value("gender") is None
        ]

        return JsonResponse(
            data=[l.to_json() for l in lemmas_with_unspecified_gender],
            safe=False,
        )
