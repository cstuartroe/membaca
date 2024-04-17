import datetime
from django.views import View
from django.http import HttpRequest, HttpResponse
from django.db import transaction
from .ajax_utils import logged_in, parse_post
from spaced_repetition.models.user import User
from spaced_repetition.models.lemma_add import LemmaAdd
from spaced_repetition.models.metadata_trial import MetadataTrial


@transaction.atomic
def create_metadata_trial(user: User, post_data: dict):
    lemma_add = LemmaAdd.objects.get(user_id=user.id, lemma_id=post_data["lemma_id"])

    trial = MetadataTrial(
        time_created=datetime.datetime.now(),
        lemma_add=lemma_add,
        metadata_field=post_data["metadata_field"],
        choices="|".join(post_data["choices"]),
        choice=post_data["choice"],
        correct=post_data["correct"],
        easiness=post_data["easiness"],
    )
    trial.save()


class MetadataTrialView(View):
    @logged_in
    @parse_post
    def post(self, request: HttpRequest, post_data: dict):
        create_metadata_trial(request.user, post_data)
        return HttpResponse(status=200)
