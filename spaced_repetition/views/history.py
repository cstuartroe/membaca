from dataclasses import dataclass
import datetime
from django.views import View
from django.http import HttpRequest, JsonResponse
from .ajax_utils import logged_in
from spaced_repetition.models.trial import Trial


@dataclass
class DailySummary:
    date: datetime.date
    new_lemmas: set[int]
    new_lemma_trials: int = 0
    review_trials: int = 0

    def to_json(self):
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "new_lemmas": len(self.new_lemmas),
            "new_lemma_trials": self.new_lemma_trials,
            "review_trials": self.review_trials,
        }


class HistoryView(View):
    @logged_in
    def get(self, request: HttpRequest):
        seen_lemmas = set()
        daily_summaries = []

        trials = (Trial.objects
                  .select_related("lemma_add")
                  .select_related("lemma_add__lemma")
                  .filter(lemma_add__user_id=request.user.id)
                  .filter(lemma_add__lemma__language_id=request.GET.get("language_id"))
                  .order_by("time_created"))

        current_day = trials[0].time_created.date()
        current_daily_summary = DailySummary(current_day, set())
        daily_summaries.append(current_daily_summary)

        for trial in trials:
            if trial.time_created.date() != current_day:
                seen_lemmas = seen_lemmas | current_daily_summary.new_lemmas
                current_day = trial.time_created.date()
                current_daily_summary = DailySummary(current_day, set())
                daily_summaries.append(current_daily_summary)

            if trial.lemma_add.lemma_id in seen_lemmas:
                current_daily_summary.review_trials += 1
            else:
                current_daily_summary.new_lemmas.add(trial.lemma_add.lemma_id)
                current_daily_summary.new_lemma_trials += 1

        return JsonResponse(
            data=[
                summary.to_json()
                for summary in daily_summaries[::-1]
            ],
            safe=False,
        )
