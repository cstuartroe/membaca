import datetime
from dataclasses import dataclass
import random
from typing import Optional, Union
from django.views import View
from django.http import HttpRequest, JsonResponse
from django.db import transaction
from .ajax_utils import logged_in
from spaced_repetition.models.user import User
from spaced_repetition.models.lemma import Lemma
from spaced_repetition.models.trial import Trial, MAX_EASINESS
from spaced_repetition.models.word_in_sentence import WordInSentence
from spaced_repetition.utils.string_utils import levenshtein
from .playing_lemmas import get_playing_lemmas


@dataclass
class CardInfo:
    lemma_id: int
    trial_type: str
    answer: Optional[WordInSentence]
    other_choices: list[str]
    recommended_easiness: int

    def to_json(self):
        if self.answer is None:
            answer = None
        else:
            answer = {
                "sentence": self.answer.sentence.to_json(),
                "slash_separated_word": self.answer.slash_separated_string(),
                "substrings": [s.to_json() for s in self.answer.substrings.all()]
            }

        return {
            "lemma_id": self.lemma_id,
            "trial_type": self.trial_type,
            "answer": answer,
            "other_choices": self.other_choices,
            "recommended_easiness": self.recommended_easiness,
        }


@dataclass
class CardSet:
    lemmas: list[Lemma]
    cards: list[CardInfo]
    more: bool

    def to_json(self):
        return {
            "lemmas_by_id": {
                lemma.id: lemma.to_json()
                for lemma in self.lemmas
            },
            "cards": [
                card.to_json()
                for card in self.cards
            ],
            "more": self.more,
        }


class CardsView(View):
    @logged_in
    def get(self, request: HttpRequest):
        card_set = self.get_cards(request.user, request.GET.get("language_id"))
        return JsonResponse(card_set.to_json())

    def get_cards(self, user: User, language_id: int) -> CardSet:
        raise NotImplemented


def random_similar(target: Lemma, choices: list[Lemma], number: int = 3) -> list[Lemma]:
    diffs: list[tuple[float, Lemma]] = [
        (levenshtein(target.citation_form, choice.citation_form), choice)
        for choice in choices
        if choice.citation_form != target.citation_form
    ]

    diffs.sort(key=lambda pair: pair[0])
    return random.sample([lemma for _, lemma in diffs[:100]], k=number)


def random_word_in_sentence(user: User, lemma: Lemma) -> WordInSentence:
    return (
        WordInSentence.objects.select_related('sentence')
        .prefetch_related('sentence__adds')
        .filter(lemma_id=lemma.id, sentence__adds__user_id=user.id)
        .order_by('?')
    )[0]


def get_translation_card(lemma: Lemma, recommended_easiness: int, all_lemmas: list[Lemma]):
    return CardInfo(
        lemma_id=lemma.id,
        trial_type=Trial.TrialType.CHOOSE_TRANSLATION.value,
        answer=None,
        other_choices=[lemma.translation for lemma in random_similar(lemma, all_lemmas)],
        recommended_easiness=recommended_easiness,
    )


def get_citation_form_card(lemma: Lemma, recommended_easiness: int, all_lemmas: list[Lemma]):
    return CardInfo(
        lemma_id=lemma.id,
        trial_type=Trial.TrialType.CHOOSE_CITATION_FORM.value,
        answer=None,
        other_choices=[lemma.citation_form for lemma in random_similar(lemma, all_lemmas)],
        recommended_easiness=recommended_easiness,
    )


def get_cloze_card(lemma: Lemma, recommended_easiness: int, playing_lemmas: list[Lemma], user: User):
    word = random_word_in_sentence(user, lemma)
    return CardInfo(
        lemma_id=lemma.id,
        trial_type=Trial.TrialType.CLOZE.value,
        answer=word,
        other_choices=[
            random_word_in_sentence(user, l).slash_separated_string()
            for l in random_similar(lemma, playing_lemmas)
        ],
        recommended_easiness=recommended_easiness,
    )


NEW_CARDS_COUNT = 5
REVIEW_CARDS_COUNT = 10


class NewCardsView(CardsView):
    @transaction.atomic
    def get_cards(self, user: User, language_id: int) -> CardSet:
        all_lemmas = list(Lemma.objects.filter(language_id=language_id))

        playing_lemmas = get_playing_lemmas(user, language_id)
        new_lemmas = [
            lemma_info
            for lemma_info in playing_lemmas
            if lemma_info.last_trial is None
        ]
        new_lemmas.sort(key=lambda lemma_info: lemma_info.due_date)
        more = len(new_lemmas) > NEW_CARDS_COUNT
        new_lemmas = new_lemmas[:NEW_CARDS_COUNT]
        random.shuffle(new_lemmas)

        cards: list[CardInfo] = []
        for lemma_info in new_lemmas:
            cards.append(get_translation_card(
                lemma_info.lemma,
                recommended_easiness=1,
                all_lemmas=all_lemmas,
            ))
        random.shuffle(new_lemmas)
        for lemma_info in new_lemmas:
            cards.append(get_citation_form_card(
                lemma_info.lemma,
                recommended_easiness=1,
                all_lemmas=all_lemmas,
            ))
        random.shuffle(new_lemmas)
        for lemma_info in new_lemmas:
            cards.append(get_cloze_card(
                lemma_info.lemma,
                recommended_easiness=1,
                playing_lemmas=[l.lemma for l in playing_lemmas],
                user=user,
            ))

        return CardSet(
            lemmas=[l.lemma for l in new_lemmas],
            cards=cards,
            more=more,
        )


TRIAL_TYPE_CYCLE = {
    Trial.TrialType.CHOOSE_TRANSLATION.value: Trial.TrialType.CHOOSE_CITATION_FORM,
    Trial.TrialType.CHOOSE_CITATION_FORM.value: Trial.TrialType.CLOZE,
    Trial.TrialType.CLOZE.value: Trial.TrialType.CHOOSE_TRANSLATION,
}


class ReviewCardsView(CardsView):
    @transaction.atomic
    def get_cards(self, user: User, language_id: int) -> CardSet:
        all_lemmas = list(Lemma.objects.filter(language_id=language_id))
        today = datetime.date.today()

        playing_lemmas = get_playing_lemmas(user, language_id)
        review_lemmas = [
            lemma_info
            for lemma_info in playing_lemmas
            if lemma_info.last_trial is not None and (lemma_info.last_trial.due_date() <= today)
        ]
        review_lemmas.sort(key=lambda lemma_info: (lemma_info.last_trial.easiness, lemma_info.due_date))
        more = len(review_lemmas) > REVIEW_CARDS_COUNT
        review_lemmas = review_lemmas[:REVIEW_CARDS_COUNT]
        random.shuffle(review_lemmas)

        cards: list[CardInfo] = []
        for lemma_info in review_lemmas:
            recommended_easiness = min(MAX_EASINESS, lemma_info.last_trial.easiness + 1)

            next_trial_type = TRIAL_TYPE_CYCLE[lemma_info.last_trial.trial_type]
            if next_trial_type is Trial.TrialType.CHOOSE_TRANSLATION:
                cards.append(get_translation_card(
                    lemma_info.lemma,
                    recommended_easiness=recommended_easiness,
                    all_lemmas=all_lemmas,
                ))
            elif next_trial_type is Trial.TrialType.CHOOSE_CITATION_FORM:
                cards.append(get_citation_form_card(
                    lemma_info.lemma,
                    recommended_easiness=recommended_easiness,
                    all_lemmas=all_lemmas,
                ))
            elif next_trial_type is Trial.TrialType.CLOZE:
                cards.append(get_cloze_card(
                    lemma_info.lemma,
                    recommended_easiness=recommended_easiness,
                    playing_lemmas=[l.lemma for l in playing_lemmas],
                    user=user,
                ))

        return CardSet(
            lemmas=[l.lemma for l in review_lemmas],
            cards=cards,
            more=more,
        )

