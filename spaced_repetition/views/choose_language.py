from django.views import View
from django.http import HttpRequest, HttpResponse
from spaced_repetition.models.language import Language
from spaced_repetition.models.user_settings import UserSettings
from .ajax_utils import parse_post


class ChooseLanguageView(View):
    @parse_post
    def post(self, request: HttpRequest, post_data):
        user_settings_list = list(UserSettings.objects.filter(user__id=request.user.id))
        if user_settings_list:
            user_settings = user_settings_list[0]
        else:
            user_settings = UserSettings(user=request.user)

        user_settings.current_language = Language.objects.get(id=post_data["language"])
        user_settings.save()

        return HttpResponse(200)
