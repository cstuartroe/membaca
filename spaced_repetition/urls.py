from django.contrib import admin
from django.urls import include, path, re_path

from .views.languages import LanguagesView
from .views.react_index import ReactIndexView
from .views.current_user_state import CurrentUserStateView
from .views.choose_language import ChooseLanguageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "google_sso/",
        include("django_google_sso.urls", namespace="django_google_sso")
    ),
    path(
        "current_user_state",
        CurrentUserStateView.as_view(),
        name="current_user_state",
    ),
    path("api/choose_language", ChooseLanguageView.as_view(), name="choose_language"),
    path("api/languages", LanguagesView.as_view(), name="languages"),
    re_path(r'^.*$', ReactIndexView.as_view(), name="react_index")
]
