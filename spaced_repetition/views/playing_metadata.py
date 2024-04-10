import datetime
from dataclasses import dataclass
from typing import Optional
from django.views import View
from django.http import HttpRequest, JsonResponse
from django.db import transaction
from .ajax_utils import logged_in
from spaced_repetition.models.user import User
from spaced_repetition.models.lemma import Lemma, is_metadata_playable
from spaced_repetition.models.lemma_add import LemmaAdd
from spaced_repetition.models.metadata_trial import MetadataTrial


@dataclass
class PlayingMetadataInfo:
    lemma: Lemma
    last_trial: Optional[MetadataTrial]
    due_date: datetime.datetime


@transaction.atomic
def get_playing_metadata(user: User, language_id: int, metadata_field: str) -> list[PlayingMetadataInfo]:
    lemma_adds: list[LemmaAdd] = []
    lemma_add_query = LemmaAdd.objects.select_related('lemma').filter(lemma__language_id=language_id, user_id=user.id)
    for lemma_add in lemma_add_query:
        lemma_adds.append(lemma_add)

    playing_lemma_info: dict[int, PlayingMetadataInfo] = {}
    for lemma_add in lemma_adds:
        if is_metadata_playable(language_id, metadata_field, lemma_add.lemma.metadata_value(metadata_field)):
            playing_lemma_info[lemma_add.lemma.id] = PlayingMetadataInfo(
                lemma=lemma_add.lemma,
                last_trial=None,
                due_date=lemma_add.time_created.date(),
            )

    trials = (
        MetadataTrial.objects
        .select_related('lemma_add')
        .select_related('lemma_add__lemma')
        .filter(metadata_field=metadata_field)
        .filter(lemma_add__lemma__language_id=language_id, lemma_add__user_id=user.id)
        .order_by('time_created')
    )
    for trial in trials:
        if trial.lemma_add.lemma_id not in playing_lemma_info:
            raise ValueError

        playing_lemma_info[trial.lemma_add.lemma_id].due_date = trial.due_date()
        playing_lemma_info[trial.lemma_add.lemma_id].last_trial = trial

    return list(playing_lemma_info.values())


class PlayingMetadataView(View):
    @logged_in
    def get(self, request: HttpRequest):
        language_id = int(request.GET.get("language_id"))
        metadata_field = request.GET.get("metadata_field")
        playing_metadata_info = get_playing_metadata(request.user, language_id, metadata_field)

        return JsonResponse(
            data=[
                {
                    "lemma_id": info.lemma.id,
                    "last_trial": info.last_trial and info.last_trial.to_json(),
                    "due_date": info.due_date.strftime("%Y-%m-%d"),
                }
                for info in playing_metadata_info
            ],
            safe=False,
        )

