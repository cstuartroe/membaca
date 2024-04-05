from django.views import View
from django.http import HttpRequest, JsonResponse
from .ajax_utils import admin_only
from spaced_repetition.models.lemma import Lemma


INDONESIAN_LANGUAGE_ID = 2


class IndonesianEView(View):
    @admin_only
    def get(self, _request: HttpRequest):
        lemmas = Lemma.objects.filter(language_id=INDONESIAN_LANGUAGE_ID).order_by("id")

        lemmas_with_plain_e = [
            lemma
            for lemma in lemmas
            if "e" in lemma.citation_form.lower()
        ]

        return JsonResponse(
            data=[l.to_json() for l in lemmas_with_plain_e],
            safe=False,
        )
