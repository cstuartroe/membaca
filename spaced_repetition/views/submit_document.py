from django.views import View
from django.http import HttpRequest, JsonResponse
from django.db import transaction

from spaced_repetition.models.language import Language
from spaced_repetition.models.document import Document
from spaced_repetition.models.sentence import Sentence
from .ajax_utils import parse_post, admin_only


@transaction.atomic
def create_document(language_id: int, title: str, link: str, sentences: list[str], translations: list[str]) -> int:
    if len(sentences) != len(translations):
        raise ValueError("Sentences and translations differ in number")

    if title == "":
        raise ValueError("Must have title")

    if link == "":
        raise ValueError("Must have link")

    if len(sentences) == 0:
        raise ValueError("Must have at least one sentence")

    language = Language.objects.get(id=language_id)
    document = Document(
        title=title,
        language=language,
        link=link,
    )
    document.save()

    for i, (text, translation) in enumerate(zip(sentences, translations)):
        sentence = Sentence(
            document=document,
            position=i,
            text=text,
            translation=translation,
        )
        sentence.save()

    return document.id


class SubmitDocumentView(View):
    @admin_only
    @parse_post
    def post(self, _request: HttpRequest, post_data):
        document_id = create_document(
            language_id=post_data["language"],
            title=post_data["title"],
            link=post_data["link"],
            sentences=post_data["sentences"],
            translations=post_data["translations"],
        )
        return JsonResponse({
            "document_id": document_id,
        })
