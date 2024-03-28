from django.views import View
from django.http import HttpRequest, JsonResponse
from .ajax_utils import logged_in
from spaced_repetition.models.lemma import Lemma


class LemmaView(View):
    @logged_in
    def get(self, request: HttpRequest):
        lemma = Lemma.objects.get(id=request.GET.get("id"))
        return JsonResponse(lemma.to_json())
