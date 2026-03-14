from core_play import views
from django.urls import path


urlpatterns = [
    path('', views.index, name="index"),
    path('music/<slug:author>/<slug:slug>', views.index, name="index_song"),
    path('authors/', views.authors, name="authors"),
    path('songs/', views.songs, name="songs"),
    path('search/', views.search, name="search"),
    path('author-info/<int:id>/', views.author_info, name="author_info"),
    path('get-author-info/<int:id>/', views.get_author_info, name="get_author_info"),
    path('get-author-songs/<int:id>/', views.get_author_songs, name="get_author_songs"),
    path('set-language/', views.set_language, name="set_language")
]
