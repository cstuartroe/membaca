from django.contrib import admin
from django.urls import include, path, re_path

from .views.languages import LanguagesView
from .views.react_index import ReactIndexView
from .views.current_user_state import CurrentUserStateView
from .views.choose_language import ChooseLanguageView
from .views.submit_document import SubmitDocumentView
from .views.document import DocumentView
from .views.documents import DocumentsView
from .views.collections import CollectionsView
from .views.sentence import SentenceView
from .views.sentence_add import SentenceAddView
from .views.word_in_sentence import WordInSentenceView
from .views.search_lemmas import SearchLemmasView
from .views.lemma import LemmaView
from .views.playing_lemmas import PlayingLemmasView
from .views.cards import NewCardsView, ReviewCardsView
from .views.trial import TrialView
from .views.history import HistoryView
from .views.indonesian_e import IndonesianEView
from .views.reading_history import ReadingHistoryView
from .views.metadata_cards import NewMetadataCardsView, ReviewMetadataCardsView
from .views.dutch_genderless_words import DutchGenderlessWordsView
from .views.metadata_trial import MetadataTrialView
from .views.playing_metadata import PlayingMetadataView
from .views.metadata_history import MetadataHistoryView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "google_sso/",
        include("django_google_sso.urls", namespace="django_google_sso")
    ),

    path("api/current_user_state", CurrentUserStateView.as_view(), name="current_user_state"),
    path("api/choose_language", ChooseLanguageView.as_view(), name="choose_language"),
    path("api/languages", LanguagesView.as_view(), name="languages"),
    path("api/submit_document", SubmitDocumentView.as_view(), name="submit_document"),
    path("api/document/<int:document_id>", DocumentView.as_view(), name="document"),
    path("api/documents", DocumentsView.as_view(), name="documents"),
    path("api/collections", CollectionsView.as_view(), name="collections"),
    path("api/sentence/<int:sentence_id>", SentenceView.as_view(), name="sentence"),
    path("api/sentence_add", SentenceAddView.as_view(), name="sentence_add"),
    path("api/words_in_sentence", WordInSentenceView.as_view(), name="words_in_sentence"),
    path("api/search_lemmas", SearchLemmasView.as_view(), name="search_lemmas"),
    path("api/lemma", LemmaView.as_view(), name="lemma"),
    path("api/playing_lemmas", PlayingLemmasView.as_view(), name="playing_lemmas"),
    path("api/cards/new", NewCardsView.as_view(), name="new_cards"),
    path("api/cards/review", ReviewCardsView.as_view(), name="review_cards"),
    path("api/trial", TrialView.as_view(), name="trial"),
    path("api/history", HistoryView.as_view(), name="history"),
    path("api/indonesian_e", IndonesianEView.as_view(), name="indonesian_e"),
    path("api/reading_history", ReadingHistoryView.as_view(), name="reading_history"),
    path("api/metadata_cards/new", NewMetadataCardsView.as_view(), name="new_metadata_cards"),
    path("api/metadata_cards/review", ReviewMetadataCardsView.as_view(), name="review_metadata_cards"),
    path("api/dutch_genderless_words", DutchGenderlessWordsView.as_view(), name="dutch_genderless_words"),
    path("api/metadata_trial", MetadataTrialView.as_view(), name="metadata_trial"),
    path("api/playing_metadata", PlayingMetadataView.as_view(), name="playing_metadata"),
    path("api/metadata_history", MetadataHistoryView.as_view(), name="metadata_history"),

    re_path(r'^.*$', ReactIndexView.as_view(), name="react_index")
]
