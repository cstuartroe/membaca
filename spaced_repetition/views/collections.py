from django.views import View
from django.http import HttpRequest, JsonResponse
from .ajax_utils import logged_in
from spaced_repetition.models.collection import Collection


class CollectionsView(View):
    @logged_in
    def get(self, request: HttpRequest):
        collections = Collection.objects.filter(language_id=request.GET.get("language_id"))
        return JsonResponse(
            data=[
                collection.to_json()
                for collection in collections
            ],
            safe=False,
        )
