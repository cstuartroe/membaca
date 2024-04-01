from django.views import View
from django.http import HttpRequest, JsonResponse

from .ajax_utils import logged_in
from spaced_repetition.models.document import Document


class DocumentsView(View):
    @logged_in
    def get(self, request: HttpRequest):
        documents = Document.objects.filter(collection_id=request.GET["collection_id"]).order_by("order").all()

        return JsonResponse([
            document.to_json()
            for document in documents
        ], safe=False)
