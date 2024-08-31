from django.views import View
from django.http import HttpRequest, JsonResponse
from .ajax_utils import logged_in
from spaced_repetition.models.user import User
from spaced_repetition.models.sentence_add import SentenceAdd
from spaced_repetition.models.word_in_sentence import WordInSentence


def is_added(word: WordInSentence, user: User):
    if word.lemma is None:
        return None

    return word.lemma.lemmaadd_set.filter(user_id=user.id).exists()


class SentenceView(View):
    @logged_in
    def get(self, request: HttpRequest, sentence_id: int):
        rows = list(SentenceAdd.objects.filter(sentence_id=sentence_id, user_id=request.user.id))
        added = len(rows) == 1

        words = (
            WordInSentence.objects
            .filter(sentence__id=sentence_id)
            .prefetch_related('substrings')
            .prefetch_related('lemma')
            .prefetch_related('lemma__lemmaadd_set')
        )

        return JsonResponse(
            data={
                "added": added,
                "words": [
                    {
                        **word.to_json(),
                        "substrings": [
                            substring.to_json()
                            for substring in word.substrings.all()
                        ],
                        "added": is_added(word, request.user),
                    }
                    for word in words
                ],
            },
        )
