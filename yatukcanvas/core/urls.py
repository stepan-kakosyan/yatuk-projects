from core import views
from django.urls import path


urlpatterns = [
    path('contact-us', views.contact_us, name="contact_us"),
    path('music', views.music, name="music"),
    path('set-language/', views.set_language, name="set_language"),
    path('set-theme/', views.set_theme, name="set_theme"),
    path('privacy-policy/', views.privacy_policy, name="privacy_policy"),
    path('terms-and-conditions/', views.terms_and_conditions, name="terms_and_conditions"),
    path('author/<str:slug>/', views.author, name="author"),
    path('author-photoarchive/<str:slug>/', views.author_photoarchive, name="author_photoarchive"),
    path('saved/', views.saved, name="saved"),
    path('game/<str:author>/<str:slug>-<int:id>/', views.game, name="game"),
    path('authors/', views.authors, name="authors"),
    path('like/<int:id>/', views.like, name="like"),
    path('favorite/<int:id>/', views.favorite, name="favorite"),
    path('comment/<int:id>/', views.comment, name="comment"),
    path('search/', views.search, name="search"),
    path('photos/', views.photos, name="photos"),
    path('photo/<str:slug>-<int:id>/', views.photo, name="photo"),
    path('remove-tags/', views.remove_tags, name="remove_tags"),
    path('get-game/<int:id>/', views.get_game, name="get_game"),
]
