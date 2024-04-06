import datetime
from dataclasses import dataclass
from django.views import View
from django.http import HttpRequest, JsonResponse
from django.db import transaction
from .ajax_utils import logged_in
from spaced_repetition.models.user import User
from spaced_repetition.models.document import Document
from spaced_repetition.models.sentence import Sentence
from spaced_repetition.models.sentence_add import SentenceAdd
from spaced_repetition.models.word_in_sentence import WordInSentence


@dataclass
class DocumentReadingHistory:
    last_read: datetime.datetime
    sentences_read: int


@dataclass
class ReadingHistory:
    document_histories: dict[int, DocumentReadingHistory]
    total_words_read: int


@transaction.atomic
def get_reading_history(user: User, language_id: int):
    history = ReadingHistory(
        document_histories={},
        total_words_read=0,
    )

    sentence_adds = (
        SentenceAdd.objects
        .select_related("sentence")
        .select_related("sentence__document")
        .select_related("sentence__document__collection")
        .filter(user=user)
        .filter(sentence__document__collection__language_id=language_id)
        .order_by("time_created")
    )

    for sentence_add in sentence_adds:
        document_id = sentence_add.sentence.document_id
        if document_id not in history.document_histories:
            history.document_histories[document_id] = DocumentReadingHistory(
                last_read=None,
                sentences_read=0,
            )
        history.document_histories[document_id].last_read = sentence_add.time_created
        history.document_histories[document_id].sentences_read += 1

        history.total_words_read += WordInSentence.objects.filter(sentence_id=sentence_add.sentence_id).count()

    return history


class ReadingHistoryView(View):
    @logged_in
    def get(self, request: HttpRequest):
        history = get_reading_history(request.user, request.GET.get("language_id"))

        document_histories_json = []

        for document_id, document_history in history.document_histories.items():
            document = Document.objects.get(id=document_id)
            num_document_sentences = Sentence.objects.filter(document_id=document_id).count()
            document_histories_json.append({
                "last_read": document_history.last_read,
                "sentences_read": document_history.sentences_read,
                "total_sentences": num_document_sentences,
                "document": document.to_json(),
            })

        document_histories_json.sort(key=lambda h: h["last_read"], reverse=True)

        return JsonResponse({
            "document_histories": document_histories_json,
            "total_words_read": history.total_words_read,
        })
