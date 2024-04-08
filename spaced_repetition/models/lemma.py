import json
from django.db import models
from .language import Language, LANGUAGE_IDS


class InvalidMetadataFieldError(ValueError):
    pass


class InvalidMetadataValueError(ValueError):
    pass


class MetadataValueEvaluator:
    @staticmethod
    def playable(value: str) -> bool:
        """Returns true if a value should be quizzed on, and
        false if not. Raises InvalidMetadataValueError if
        invalid.
        """
        raise NotImplemented

    @staticmethod
    def choices(lemma: "Lemma") -> list[str]:
        raise NotImplemented


class DutchGenderEvaluator(MetadataValueEvaluator):
    @staticmethod
    def playable(value: str) -> bool:
        if value in ("de", "het"):
            return True
        elif value in ("-", None):
            return False
        else:
            raise InvalidMetadataValueError

    @staticmethod
    def choices(_: "Lemma") -> list[str]:
        return ["de", "het"]


METADATA_FIELD_EVALUATORS: dict[int, dict[str, MetadataValueEvaluator]] = {
    LANGUAGE_IDS["Dutch"]: {
        "gender": DutchGenderEvaluator,
    },
    LANGUAGE_IDS["Indonesian"]: {},
}


def is_metadata_playable(language_id: int, metadata_field: str, metadata_value: str) -> bool:
    if metadata_field not in METADATA_FIELD_EVALUATORS[language_id]:
        raise InvalidMetadataFieldError

    evaluator = METADATA_FIELD_EVALUATORS[language_id][metadata_field]
    return evaluator.playable(metadata_value)


class Lemma(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    citation_form = models.CharField(max_length=32)
    translation = models.CharField(max_length=128)

    # This field is used to store information about, e.g.,
    # noun gender, irregular conjugations, etc. as json
    # Its usage is language-specific.
    metadata = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"{self.language.name} lemma {self.citation_form} \"{self.translation}\""

    def to_json(self):
        return {
            "id": self.id,
            "language_id": self.language_id,
            "citation_form": self.citation_form,
            "translation": self.translation,
            "metadata": self.parse_metadata(),
        }

    def parse_metadata(self):
        return json.loads(self.metadata or "{}")

    def metadata_value(self, metadata_field: str):
        return self.parse_metadata().get(metadata_field, None)

    def set_metadata_field(self, metadata_field: str, metadata_value: str):
        # just to see if errors are raised
        is_metadata_playable(self.language_id, metadata_field, metadata_value)

        self.metadata = json.dumps(
            obj={
                **self.parse_metadata(),
                metadata_field: metadata_value,
            },
            sort_keys=True,
        )
