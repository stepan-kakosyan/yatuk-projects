from core import views
from django.urls import path


urlpatterns = [
    path('', views.index, name="index"),
    path('contact-us', views.contact_us, name="contact_us"),
    path('music', views.music, name="music"),
    path('set-language/', views.set_language, name="set_language"),
    path('set-theme/', views.set_theme, name="set_theme"),
    path('privacy-policy/', views.privacy_policy, name="privacy_policy"),
    path('terms-and-conditions/',
         views.terms_and_conditions, name="terms_and_conditions"),
    path('author/<str:slug>/<slug:genre>/', views.author, name="author"),
    path('author-bio/<str:slug>/', views.author_bio, name="author_bio"),
    path('author-quotes/<str:slug>/', views.author_quotes,
         name="author_quotes"),
    path('author-photoarchive/<str:slug>/',
         views.author_photoarchive, name="author_photoarchive"),
    path('saved/', views.saved, name="saved"),
    path('want-read/', views.want_read, name="want_read"),
    path('poem/<str:author>/<str:slug>-<int:id>/', views.poem, name="poem"),
    path('reading-poem/<int:id>/', views.reading_poem, name="reading_poem"),
    path('authors/', views.authors, name="authors"),
    path('like/<int:id>/', views.like, name="like"),
    path('favorite/<int:id>/', views.favorite, name="favorite"),
    path('want-to-read/<int:id>/', views.want_to_read, name="want_to_read"),
    path('download-pdf/<int:id>/', views.html2pdf, name="html2pdf"),
    path('comment/<int:id>/', views.comment, name="comment"),
    path('search/', views.search, name="search"),
    path('photos/', views.photos, name="photos"),
    path('photo/<str:slug>-<int:id>/', views.photo, name="photo"),
    path('remove-tags/', views.remove_tags, name="remove_tags"),
]
