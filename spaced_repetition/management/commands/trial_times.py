from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt

from spaced_repetition.models.trial import Trial


MAXIMUM_SECONDS = 40


class Command(BaseCommand):
    help = 'Shows a histogram of time between trials'

    def add_arguments(self, parser):
        parser.add_argument("-u", "--user_id", required=True)

    def handle(self, *args, **options):
        trials = list(
            Trial.objects.select_related('lemma_add')
            .filter(lemma_add__user_id=options["user_id"]).
            order_by('time_created')
        )

        seconds_taken = [
            min(round((t2.time_created - t1.time_created).total_seconds()), MAXIMUM_SECONDS)
            for t1, t2 in zip(trials[:-1], trials[1:])
        ]

        histogram = {
            seconds: 0
            for seconds in range(MAXIMUM_SECONDS + 1)
        }

        for s in seconds_taken:
            histogram[s] += 1

        plt.bar(*zip(*histogram.items()))
        plt.show()
