from django.views import View
from django.http import HttpRequest, JsonResponse

from .ajax_utils import logged_in
from spaced_repetition.models.document import Document


class DocumentsView(View):
    @logged_in
    def get(self, request: HttpRequest):
        documents = Document.objects.filter(language__id=request.GET["language_id"]).order_by("id").all()

        return JsonResponse([
            document.to_json()
            for document in documents
        ], safe=False)
