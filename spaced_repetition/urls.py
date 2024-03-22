from django.contrib import admin
from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "google_sso/",
        include("django_google_sso.urls", namespace="django_google_sso")
    ),
    path("languages", views.languages, name="languages"),
    re_path(r'^.*$', views.react_index, name="react_index")
]
