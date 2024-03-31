import datetime
from dataclasses import dataclass
from typing import Optional
from django.views import View
from django.http import HttpRequest, JsonResponse
from django.db import transaction
from .ajax_utils import logged_in
from spaced_repetition.models.user import User
from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.lemma_add import LemmaAdd
from spaced_repetition.models.trial import Trial


@dataclass
class PlayingLemmaInfo:
    lemma: Lemma
    last_trial: Optional[Trial]
    due_date: datetime.datetime


@transaction.atomic
def get_playing_lemmas(user: User, language_id: int) -> list[PlayingLemmaInfo]:
    playing_lemma_info: dict[int, PlayingLemmaInfo] = {}

    lemma_adds = LemmaAdd.objects.select_related('lemma').filter(lemma__language_id=language_id, user_id=user.id)
    for lemma_add in lemma_adds:
        playing_lemma_info[lemma_add.lemma_id] = PlayingLemmaInfo(
            lemma=lemma_add.lemma,
            due_date=lemma_add.time_created.date(),
            last_trial=None,
        )

    trials = (Trial.objects.select_related('lemma_add').select_related('lemma_add__lemma')
              .filter(lemma_add__lemma__language_id=language_id, lemma_add__user_id=user.id).order_by('time_created'))
    for trial in trials:
        if trial.lemma_add.lemma_id not in playing_lemma_info:
            raise ValueError

        playing_lemma_info[trial.lemma_add.lemma_id].due_date = trial.due_date()
        playing_lemma_info[trial.lemma_add.lemma_id].last_trial = trial

    return list(playing_lemma_info.values())


class PlayingLemmasView(View):
    @logged_in
    def get(self, request: HttpRequest):
        language_id = request.GET.get("language_id")
        playing_lemma_info = get_playing_lemmas(request.user, language_id)

        return JsonResponse(
            data=[
                {
                    "lemma_id": info.lemma.id,
                    "last_trial": info.last_trial and info.last_trial.to_json(),
                    "due_date": info.due_date.strftime("%Y-%m-%d"),
                }
                for info in playing_lemma_info
            ],
            safe=False,
        )

