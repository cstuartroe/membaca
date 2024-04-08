from django.views import View
from django.http import HttpRequest, HttpResponse, JsonResponse
from .ajax_utils import logged_in, admin_only, parse_post
from spaced_repetition.models.lemma import Lemma


class LemmaView(View):
    @logged_in
    def get(self, request: HttpRequest):
        lemma = Lemma.objects.get(id=request.GET.get("id"))
        return JsonResponse(lemma.to_json())

    @admin_only
    @parse_post
    def post(self, request: HttpRequest, post_data):
        lemma = Lemma.objects.get(id=post_data["id"])

        citation_form = post_data.get("citation_form", None)
        if citation_form:
            lemma.citation_form = citation_form

        gender = post_data.get("metadata:gender", None)
        if gender:
            lemma.set_metadata_field("gender", gender)

        lemma.save()
        return HttpResponse(200)
