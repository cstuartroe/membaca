from django.views import View
from django.http import HttpRequest, JsonResponse
from spaced_repetition.models.word import Word
from .ajax_utils import logged_in
from spaced_repetition.utils.string_utils import levenshtein


class SearchLemmasView(View):
    @logged_in
    def get(self, request: HttpRequest):
        language_id = request.GET.get("language_id")
        search_string = request.GET.get("q").lower()
        num_results = int(request.GET.get("num_results", 5))

        words_and_edit_distance: list[tuple[str, float]] = [
            (word, levenshtein(search_string, word.word.lower()))
            for word in Word.objects.filter(language_id=language_id)
        ]
        words_and_edit_distance.sort(key=lambda pair: pair[1])

        lemma_ids = set()
        lemmas = []
        for word, _ in words_and_edit_distance:
            if word.lemma_id in lemma_ids:
                continue

            lemma_ids.add(word.lemma_id)
            lemmas.append(word.lemma)

            if len(lemmas) == num_results:
                break

        return JsonResponse(
            data=[
                lemma.to_json()
                for lemma in lemmas
            ],
            safe=False,
        )


