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
            occurrences=0,
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
    matching_word = list(Word.objects.filter(word=word_text, lemma_id=lemma_id))

    if not matching_word:
        word = Word(
            word=word_text,
            language_id=language_id,
            lemma_id=lemma_id,
            occurrences=1,
        )
        word.save()
    else:
        word = matching_word[0]
        word.occurrences += 1
        word.save()



class WordInSentenceView(View):
    @admin_only
    @parse_post
    def post(self, _request: HttpRequest, post_data):
        create_word_in_sentence(post_data)
        return HttpResponse(status=200)
