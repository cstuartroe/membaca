from django.views import View
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db import transaction

from .ajax_utils import logged_in, admin_only
from spaced_repetition.models.sentence import Sentence
from spaced_repetition.models.word_in_sentence import WordInSentence, Substring


@transaction.atomic
def create_word_in_sentence(data: dict):
    sentence = Sentence.objects.get(id=data["sentence_id"])

    word = WordInSentence(
        lemma__id=data["lemma_id"],
        sentence=sentence,
    )
    word.save()
    for substring_data in data["substrings"]:
        start = substring_data["start"]
        end = substring_data["end"]

        if start <= end:
            raise ValueError
        elif end > len(sentence.text):
            raise ValueError

        substring = Substring(
            start=start,
            end=end,
            word__id=data["id"],
        )
        substring.save()


class WordsInSentenceView(View):
    @logged_in
    def get(self, _request: HttpRequest):
        sentence_id = _request.GET.get("sentence_id")

        words = WordInSentence.objects.filter(sentence__id=sentence_id).prefetch_related('substrings')

        return JsonResponse(
            data=[
                {
                    **word.to_json(),
                    "substrings": [
                        substring.to_json()
                        for substring in word.substrings.all()
                    ],
                }
                for word in words
            ],
            safe=False,
        )

    @admin_only
    def post(self, _request: HttpRequest, post_data):
        create_word_in_sentence(post_data)
        return HttpResponse(200)
