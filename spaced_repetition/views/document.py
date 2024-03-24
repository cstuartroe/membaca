from django.views import View
from django.http import HttpRequest, JsonResponse

from .ajax_utils import logged_in
from spaced_repetition.models.document import Document
from spaced_repetition.models.sentence import Sentence


class DocumentView(View):
    @logged_in
    def get(self, request: HttpRequest, document_id: int):
        document = Document.objects.get(id=document_id)
        sentences = Sentence.objects.filter(document=document).order_by("position").all()

        data = document.to_json()
        data["sentences"] = [
            sentence.to_json()
            for sentence in sentences
        ]

        return JsonResponse(data)
