import datetime
from dataclasses import dataclass
from typing import Optional
from django.views import View
from django.http import HttpRequest, JsonResponse
from .ajax_utils import logged_in
from spaced_repetition.models.lemma_add import LemmaAdd
from spaced_repetition.models.trial import Trial


@dataclass
class PlayingLemmaInfo:
    easiness: int
    due_date: datetime.date
    last_trial_type: Optional[str]

    def to_json(self):
        return {
            "easiness": self.easiness,
            "due_date": self.due_date.strftime("%Y-%m-%d"),
            "last_trial_type": self.last_trial_type,
        }


class PlayingLemmasView(View):
    @logged_in
    def get(self, request: HttpRequest):
        today = datetime.date.today()
        playing_lemma_info: dict[int, PlayingLemmaInfo] = {}

        lemma_adds = LemmaAdd.objects.filter(user_id=request.user.id)
        for lemma_add in lemma_adds:
            playing_lemma_info[lemma_add.lemma_id] = PlayingLemmaInfo(0, today, None)

        trials = Trial.objects.select_related('lemma_add').filter(lemma_add__user_id=request.user.id).order_by('time_created')
        for trial in trials:
            if trial.lemma_add.lemma_id not in playing_lemma_info:
                raise ValueError

            playing_lemma_info[trial.lemma_add.lemma_id] = PlayingLemmaInfo(trial.easiness, trial.due_date(), trial.trial_type)

        return JsonResponse(
            data=[
                {
                    "lemma_id": lemma_id,
                    **info.to_json(),
                }
                for lemma_id, info in playing_lemma_info.items()
            ],
            safe=False,
        )

