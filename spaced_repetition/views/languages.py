from django.views import View
from django.http import JsonResponse
from spaced_repetition.models.language import Language


class LanguagesView(View):
    def get(self, _request):
        return JsonResponse(
            data=[
                language.to_json()
                for language in Language.objects.all()
            ],
            safe=False,
        )
