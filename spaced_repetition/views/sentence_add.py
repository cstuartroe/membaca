import datetime
from django.views import View
from django.http import HttpRequest, HttpResponse
from django.db import transaction, utils as db_utils
from .ajax_utils import logged_in, parse_post
from spaced_repetition.models.word_in_sentence import WordInSentence
from spaced_repetition.models.lemma_add import LemmaAdd
from spaced_repetition.models.sentence_add import SentenceAdd


@transaction.atomic
def add_sentence(sentence_id: int, user_id: int):
    creation_time = datetime.datetime.utcnow()

    words = WordInSentence.objects.filter(sentence_id=sentence_id)
    for word in words:
        if word.lemma_id is not None:
            rows = list(LemmaAdd.objects.filter(lemma_id=word.lemma_id, user_id=user_id))
            if len(rows) == 0:
                lemma_add = LemmaAdd(
                    lemma_id=word.lemma_id,
                    user_id=user_id,
                    time_created=creation_time,
                )
                lemma_add.save()

    sadd = SentenceAdd(
        user_id=user_id,
        sentence_id=sentence_id,
        time_created=creation_time,
    )
    sadd.save()


class SentenceAddView(View):
    @logged_in
    @parse_post
    def post(self, request: HttpRequest, post_data):
        add_sentence(post_data["sentence_id"], request.user.id)
        return HttpResponse(status=200)
