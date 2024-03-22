from django.contrib import admin
from django.urls import include, path, re_path

from .views.languages import LanguagesView
from .views.react_index import ReactIndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "google_sso/",
        include("django_google_sso.urls", namespace="django_google_sso")
    ),
    path("languages", LanguagesView.as_view(), name="languages"),
    re_path(r'^.*$', ReactIndexView.as_view(), name="react_index")
]
