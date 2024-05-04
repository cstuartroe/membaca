import datetime
from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt
from spaced_repetition.models.language import LANGUAGE_IDS
from spaced_repetition.models.user import User
from spaced_repetition.views.reading_history import get_reading_history


class Command(BaseCommand):
    help = 'Shows cumulative words read'

    def add_arguments(self, parser):
        parser.add_argument("-l", "--language", required=True)
        parser.add_argument("-u", "--user_id", required=True)

    def handle(self, *args, **options):
        language_id = LANGUAGE_IDS[options["language"]]

        reading_history = get_reading_history(User.objects.get(id=options["user_id"]), language_id=language_id)
        first_day = min(reading_history.words_read_by_day.keys())

        cumulative_read = 0
        cumulative_read_by_day = []
        current_day = first_day
        while current_day <= datetime.date.today():
            cumulative_read += reading_history.words_read_by_day.get(current_day, 0)
            cumulative_read_by_day.append((current_day, cumulative_read))
            current_day += datetime.timedelta(days=1)

        plt.plot(*zip(*cumulative_read_by_day), marker='o')
        plt.show()
