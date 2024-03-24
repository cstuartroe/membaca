from django.contrib import admin
from django.urls import include, path, re_path

from .views.languages import LanguagesView
from .views.react_index import ReactIndexView
from .views.current_user_state import CurrentUserStateView
from .views.choose_language import ChooseLanguageView
from .views.submit_document import SubmitDocumentView
from .views.document import DocumentView
from .views.documents import DocumentsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "google_sso/",
        include("django_google_sso.urls", namespace="django_google_sso")
    ),

    path(
        "api/current_user_state",
        CurrentUserStateView.as_view(),
        name="current_user_state",
    ),
    path("api/choose_language", ChooseLanguageView.as_view(), name="choose_language"),
    path("api/languages", LanguagesView.as_view(), name="languages"),
    path("api/submit_document", SubmitDocumentView.as_view(), name="submit_document"),
    path("api/document/<int:document_id>", DocumentView.as_view(), name="document"),
    path("api/documents", DocumentsView.as_view(), name="document"),

    re_path(r'^.*$', ReactIndexView.as_view(), name="react_index")
]
