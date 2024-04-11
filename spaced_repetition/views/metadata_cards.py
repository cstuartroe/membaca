import datetime
from dataclasses import dataclass
from typing import Optional
from django.views import View
from django.http import HttpRequest, JsonResponse
from django.db import transaction
from .ajax_utils import logged_in
from spaced_repetition.models.user import User
from spaced_repetition.models.lemma import Lemma, METADATA_FIELD_EVALUATORS, is_metadata_playable
from spaced_repetition.models.metadata_trial import MetadataTrial
from spaced_repetition.models.trial import MAX_EASINESS
from .playing_lemmas import get_playing_lemmas


@dataclass
class MetadataCardInfo:
    lemma: Lemma
    choices: list[str]
    recommended_easiness: int

    def to_json(self):
        return {
            "lemma": self.lemma.to_json(),
            "choices": self.choices,
            "recommended_easiness": self.recommended_easiness,
        }


@dataclass
class MetadataCardSet:
    cards: list[MetadataCardInfo]
    more: bool

    def to_json(self):
        return {
            "cards": [
                card.to_json()
                for card in self.cards
            ],
            "more": self.more,
        }


@dataclass
class PlayingMetadataInfo:
    lemma: Lemma
    last_trial: Optional[MetadataTrial]
    due_date: datetime.date


def get_playing_metadata_info(lemmas: list[Lemma], user: User, language_id: int, metadata_field: str):
    today = datetime.date.today()
    info_by_lemma_id = {
        lemma.id: PlayingMetadataInfo(lemma, None, today)
        for lemma in lemmas
    }

    metadata_trials = (
        MetadataTrial.objects
        .select_related("lemma_add")
        .select_related("lemma_add__lemma")
        .filter(lemma_add__user_id=user.id)
        .filter(lemma_add__lemma__language_id=language_id)
        .filter(metadata_field=metadata_field)
        .order_by("time_created")
    )

    for trial in metadata_trials:
        info = info_by_lemma_id[trial.lemma_add.lemma_id]
        info.last_trial = trial
        info.due_date = trial.due_date()

    return sorted(
        list(info_by_lemma_id.values()),
        key=lambda info: info.due_date,
    )


def get_playable_metadata_infos(user: User, language_id: int, metadata_field: str) -> list[PlayingMetadataInfo]:
    playing_lemmas = [
        lemma_info.lemma
        for lemma_info in get_playing_lemmas(user, language_id)
    ]

    relevant_lemmas = [
        lemma
        for lemma in playing_lemmas
        if is_metadata_playable(language_id, metadata_field, lemma.metadata_value(metadata_field))
    ]

    return get_playing_metadata_info(relevant_lemmas, user, language_id, metadata_field)


class MetadataCardsView(View):
    @logged_in
    def get(self, request: HttpRequest):
        card_set = self.get_cards(
            user=request.user,
            language_id=int(request.GET.get("language_id")),
            metadata_field=request.GET.get("metadata_field"),
        )
        return JsonResponse(card_set.to_json())

    def get_cards(self, user: User, language_id: int, metadata_field: str) -> MetadataCardSet:
        raise NotImplemented


NEW_CARDS_COUNT = 5
REVIEW_CARDS_COUNT = 10


class NewMetadataCardsView(MetadataCardsView):
    @transaction.atomic
    def get_cards(self, user: User, language_id: int, metadata_field: str) -> MetadataCardSet:
        infos = get_playable_metadata_infos(user, language_id, metadata_field)
        unplayed_metadata_infos = [
            info
            for info in infos
            if info.last_trial is None
        ]
        more = len(unplayed_metadata_infos) > NEW_CARDS_COUNT
        lemmas_to_play = [info.lemma for info in unplayed_metadata_infos[:NEW_CARDS_COUNT]]
        evaluator = METADATA_FIELD_EVALUATORS[language_id][metadata_field]
        return MetadataCardSet(
            cards=[
                MetadataCardInfo(
                    lemma=lemma,
                    choices=evaluator.choices(lemma),
                    recommended_easiness=1,
                )
                for lemma in lemmas_to_play
            ],
            more=more,
        )


class ReviewMetadataCardsView(MetadataCardsView):
    @transaction.atomic
    def get_cards(self, user: User, language_id: int, metadata_field: str) -> MetadataCardSet:
        infos = get_playable_metadata_infos(user, language_id, metadata_field)
        today = datetime.date.today()
        review_metadata_info = [
            info
            for info in infos
            if (info.last_trial is not None) and (info.due_date <= today)
        ]
        more = len(review_metadata_info) > REVIEW_CARDS_COUNT
        infos_to_play = review_metadata_info[:REVIEW_CARDS_COUNT]
        evaluator = METADATA_FIELD_EVALUATORS[language_id][metadata_field]
        return MetadataCardSet(
            cards=[
                MetadataCardInfo(
                    lemma=info.lemma,
                    choices=evaluator.choices(info.lemma),
                    recommended_easiness=min(MAX_EASINESS, info.last_trial.easiness + 1)
                )
                for info in infos_to_play
            ],
            more=more,
        )
