from django.core.management.base import BaseCommand

from spaced_repetition.models.language import Language, LANGUAGE_IDS


class Command(BaseCommand):
    help = 'Populates all languages'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for language_name, language_id in LANGUAGE_IDS.items():
            languages = list(Language.objects.filter(id=language_id))
            if languages:
                language = languages[0]
                if language.name != language_name:
                    raise ValueError(
                        "Incorrect language mapping: Language row"
                        f" with id {language_id} has name "
                        f"{language.name} (expected {language_name})"
                    )
            else:
                language = Language(id=language_id, name=language_name)
                language.save()

