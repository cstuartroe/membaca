from dataclasses import dataclass
from django.views import View
from django.http import HttpRequest, JsonResponse
from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.word import Word
from .ajax_utils import logged_in
from spaced_repetition.utils.string_utils import levenshtein


@dataclass
class SearchResult:
    lemma: Lemma | None
    exact_match: bool

    def to_json(self):
        return {
            "lemma": self.lemma and self.lemma.to_json(),
            "exact_match": self.exact_match,
        }


def get_search_results(language_id: int, search_string: str, num_results: int) -> tuple[list[SearchResult], bool]:
    words_and_edit_distance: list[tuple[str, float]] = [
        (word, levenshtein(search_string, word.word.lower()))
        for word in Word.objects.filter(language_id=language_id)
    ]
    words_and_edit_distance.sort(key=lambda pair: (pair[1], -pair[0].occurrences))

    lemma_ids = set()
    results: list[SearchResult] = []
    no_lemma_matched = False
    for word, edit_distance in words_and_edit_distance:
        if word.lemma_id in lemma_ids:
            continue

        if word.lemma_id is None:
            if edit_distance == 0:
                no_lemma_matched = True

            continue

        lemma_ids.add(word.lemma_id)

        results.append(
            SearchResult(
                lemma=word.lemma,
                exact_match=(edit_distance == 0),
            ),
        )

        if len(results) == num_results:
            break

    return results, no_lemma_matched


class SearchLemmasView(View):
    @logged_in
    def get(self, request: HttpRequest):
        language_id = request.GET.get("language_id")
        search_string = request.GET.get("q").lower()
        num_results = int(request.GET.get("num_results", 5))

        results, no_lemma_matched = get_search_results(language_id, search_string, num_results)

        return JsonResponse(
            data={
                "results": [
                    result.to_json()
                    for result in results
                ],
                "no_lemma_matched": no_lemma_matched,
            }
        )


