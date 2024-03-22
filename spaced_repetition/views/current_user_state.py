from django.views import View
from django.http import HttpRequest, JsonResponse
from spaced_repetition.models.user_settings import UserSettings
from spaced_repetition.models.user import user_to_json


class CurrentUserStateView(View):
    def get(self, request: HttpRequest):
        if not request.user.is_active:
            return JsonResponse({
                "user": None,
                "current_language": None,
            })

        user_settings_list = list(UserSettings.objects.filter(user__id=request.user.id))
        if user_settings_list:
            current_language_json = user_settings_list[0].current_language.to_json()
        else:
            current_language_json = None

        return JsonResponse({
            "user": user_to_json(request.user),
            "current_language": current_language_json,
        })
