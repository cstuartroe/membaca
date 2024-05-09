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


@dataclass
class MetadataPlaySummary:
    playing_metadata: list[PlayingMetadataInfo]
    not_playable: int
    unannotated: int

    def to_json(self):
        return {
            "playing_metadata": [
                {
                    "lemma_id": info.lemma.id,
                    "last_trial": info.last_trial and info.last_trial.to_json(),
                    "due_date": info.due_date.strftime("%Y-%m-%d"),
                }
                for info in self.playing_metadata
            ],
            "not_playable": self.not_playable,
            "unannotated": self.unannotated,
        }


@transaction.atomic
def get_playing_metadata(user: User, language_id: int, metadata_field: str) -> MetadataPlaySummary:
    lemma_adds: list[LemmaAdd] = []
    lemma_add_query = LemmaAdd.objects.select_related('lemma').filter(lemma__language_id=language_id, user_id=user.id)
    for lemma_add in lemma_add_query:
        lemma_adds.append(lemma_add)

    playing_lemma_info: dict[int, PlayingMetadataInfo] = {}
    not_playable = 0
    unannotated = 0
    for lemma_add in lemma_adds:
        metadata_value = lemma_add.lemma.metadata_value(metadata_field)
        if metadata_value is None:
            unannotated += 1
        elif is_metadata_playable(language_id, metadata_field, metadata_value):
            playing_lemma_info[lemma_add.lemma.id] = PlayingMetadataInfo(
                lemma=lemma_add.lemma,
                last_trial=None,
                due_date=lemma_add.time_created.date(),
            )
        else:
            not_playable += 1

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

    return MetadataPlaySummary(
        playing_metadata=list(playing_lemma_info.values()),
        not_playable=not_playable,
        unannotated=unannotated,
    )


class PlayingMetadataView(View):
    @logged_in
    def get(self, request: HttpRequest):
        language_id = int(request.GET.get("language_id"))
        metadata_field = request.GET.get("metadata_field")
        metadata_summary = get_playing_metadata(request.user, language_id, metadata_field)

        return JsonResponse(metadata_summary.to_json())

