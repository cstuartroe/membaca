from django.views import View
from django.http import HttpRequest, JsonResponse
from .ajax_utils import admin_only
from spaced_repetition.models.language import LANGUAGE_IDS
from spaced_repetition.models.lemma_add import LemmaAdd


DUTCH_LANGUAGE_ID = LANGUAGE_IDS["Dutch"]


class DutchGenderlessWordsView(View):
    @admin_only
    def get(self, request: HttpRequest):
        lemma_adds = (
                     LemmaAdd.objects
                     .filter(user_id=request.user.id)
                     .select_related('lemma')
                     .filter(lemma__language_id=DUTCH_LANGUAGE_ID)
                     .order_by("id")
        )

        lemmas_with_unspecified_gender = [
            lemma_add.lemma
            for lemma_add in lemma_adds
            if lemma_add.lemma.metadata_value("gender") is None
        ]

        return JsonResponse(
            data=[l.to_json() for l in lemmas_with_unspecified_gender],
            safe=False,
        )
