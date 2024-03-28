from django.views import View
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db import transaction

from .ajax_utils import logged_in, admin_only, parse_post
from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.sentence import Sentence
from spaced_repetition.models.word_in_sentence import WordInSentence, Substring
from spaced_repetition.models.word import Word


@transaction.atomic
def create_word_in_sentence(data: dict):
    sentence = Sentence.objects.get(id=data["sentence_id"])
    language_id = data["language_id"]

    if "lemma" in data:
        citation_form = data["lemma"]["citation_form"]
        lemma = Lemma(
            language_id=language_id,
            citation_form=citation_form,
            translation=data["lemma"]["translation"],
        )
        lemma.save()
        lemma_id = lemma.id

        word = Word(
            word=citation_form,
            language_id=language_id,
            lemma_id=lemma_id,
        )
        word.save()
    elif "lemma_id" in data:
        citation_form = None
        lemma_id = data["lemma_id"]
    else:
        citation_form = None
        lemma_id = None

    word_in_sentence = WordInSentence(
        lemma_id=lemma_id,
        sentence=sentence,
    )
    word_in_sentence.save()

    word_pieces = []
    for substring_data in data["substrings"]:
        start = substring_data["start"]
        end = substring_data["end"]

        if start >= end:
            raise ValueError
        elif end > len(sentence.text):
            raise ValueError

        substring = Substring(
            start=start,
            end=end,
            word_id=word_in_sentence.id,
        )
        substring.save()

        word_pieces.append(sentence.text[substring.start:substring.end])

    word_text = ' '.join(word_pieces)
    if word_text != citation_form and lemma_id is not None:
        word = Word(
            word=word_text,
            language_id=language_id,
            lemma_id=lemma_id,
        )
        word.save()


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
    @parse_post
    def post(self, _request: HttpRequest, post_data):
        create_word_in_sentence(post_data)
        return HttpResponse(200)
