from dataclasses import dataclass
import datetime
from django.views import View
from django.http import HttpRequest, JsonResponse
from .ajax_utils import logged_in
from spaced_repetition.models.metadata_trial import MetadataTrial


MAXIMUM_TRIAL_TIME = datetime.timedelta(seconds=10)


@dataclass
class DailyMetadataActivity:
    date: datetime.date
    new_lemmas: set[int]
    new_lemma_trials: list[MetadataTrial]
    review_trials: list[MetadataTrial]
    time_taken: datetime.timedelta

    @classmethod
    def new(cls, date: datetime.date):
        return cls(date, set(), [], [], datetime.timedelta(0))

    def summary(self):
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "new_lemmas": len(self.new_lemmas),
            "new_lemma_trials": len(self.new_lemma_trials),
            "review_trials": len(self.review_trials),
            "seconds_taken": self.time_taken.total_seconds(),
        }


class MetadataHistoryView(View):
    @logged_in
    def get(self, request: HttpRequest):
        seen_lemmas = set()
        daily_summaries: list[dict] = []

        trials = (MetadataTrial.objects
                  .select_related("lemma_add")
                  .select_related("lemma_add__lemma")
                  .filter(lemma_add__user_id=request.user.id)
                  .filter(lemma_add__lemma__language_id=request.GET.get("language_id"))
                  .filter(metadata_field=request.GET.get("metadata_field"))
                  .order_by("time_created"))

        current_day = trials[0].time_created.date()
        current_daily_activity = DailyMetadataActivity.new(current_day)
        last_trial_time = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

        for trial in trials:
            if trial.time_created.date() != current_day:
                seen_lemmas = seen_lemmas | current_daily_activity.new_lemmas
                daily_summaries.append(current_daily_activity.summary())
                current_day = trial.time_created.date()
                current_daily_activity = DailyMetadataActivity.new(current_day)

            if trial.lemma_add.lemma_id in seen_lemmas:
                current_daily_activity.review_trials.append(trial)
            else:
                current_daily_activity.new_lemmas.add(trial.lemma_add.lemma_id)
                current_daily_activity.new_lemma_trials.append(trial)

            current_daily_activity.time_taken += min(
                MAXIMUM_TRIAL_TIME,
                trial.time_created - last_trial_time
            )
            last_trial_time = trial.time_created

        daily_summaries.append(current_daily_activity.summary())

        return JsonResponse({
            "summaries": daily_summaries[::-1],
        })
