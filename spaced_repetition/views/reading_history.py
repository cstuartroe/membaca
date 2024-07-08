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
    words_read_by_day: dict[datetime.date, int]
    new_lemmas_by_day: dict[datetime.date, int]
    added_lemmas_by_day: dict[datetime, int]


MAXIMUM_SECONDS_SPENT = 180


@transaction.atomic
def get_reading_history(user: User, language_id: int):
    history = ReadingHistory(
        document_histories={},
        words_read_by_day={},
        added_lemmas_by_day={},
        new_lemmas_by_day={},
    )
    seen_lemma_ids = set()
    added_lemma_ids = set()

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

        date = sentence_add.time_created.date()
        words_in_sentence = list(WordInSentence.objects.filter(sentence_id=sentence_add.sentence_id))
        history.words_read_by_day[date] = history.words_read_by_day.get(date, 0) + len(words_in_sentence)

        if date not in history.new_lemmas_by_day:
            history.new_lemmas_by_day[date] = 0
            history.added_lemmas_by_day[date] = 0
        for word in words_in_sentence:
            if word.lemma_id is None:
                pass
            elif word.lemma_id not in seen_lemma_ids:
                seen_lemma_ids.add(word.lemma_id)
                history.new_lemmas_by_day[date] += 1
            elif word.lemma_id not in added_lemma_ids:
                added_lemma_ids.add(word.lemma_id)
                history.added_lemmas_by_day[date] += 1

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

        words_read_by_day_json = []
        for date, words in history.words_read_by_day.items():
            words_read_by_day_json.append({
                "date": date,
                "words": words,
                "new_lemmas": history.new_lemmas_by_day[date],
                "added_lemmas": history.added_lemmas_by_day[date],
            })
        words_read_by_day_json.sort(key=lambda d: d["date"], reverse=True)

        return JsonResponse({
            "document_histories": document_histories_json,
            "words_read_by_day": words_read_by_day_json,
        })
