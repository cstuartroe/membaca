import datetime
from django.views import View
from django.http import HttpRequest, HttpResponse
from django.db import transaction
from .ajax_utils import logged_in, parse_post
from spaced_repetition.models.word_in_sentence import WordInSentence
from spaced_repetition.models.lemma_add import LemmaAdd
from spaced_repetition.models.sentence_add import SentenceAdd


@transaction.atomic
def add_sentence(sentence_id: int, user_id: int):
    seen_lemma_ids = set()
    for sentence_add in (
        SentenceAdd.objects.filter(user_id=user_id)
        .select_related('sentence')
        .prefetch_related('sentence__words_in_sentence')
    ):
        for word in sentence_add.sentence.words_in_sentence.all():
            if word.lemma_id is None:
                continue

            seen_lemma_ids.add(word.lemma_id)

    creation_time = datetime.datetime.utcnow()

    words = WordInSentence.objects.filter(sentence_id=sentence_id)
    for word in words:
        if word.lemma is None:
            continue

        if word.lemma_id in seen_lemma_ids:
            rows = list(LemmaAdd.objects.filter(lemma_id=word.lemma_id, user_id=user_id))
            if len(rows) == 0:
                lemma_add = LemmaAdd(
                    lemma_id=word.lemma_id,
                    user_id=user_id,
                    time_created=creation_time,
                )
                lemma_add.save()
        else:
            # just in case the word appears for the first time twice in one sentence
            seen_lemma_ids.add(word.lemma_id)

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
