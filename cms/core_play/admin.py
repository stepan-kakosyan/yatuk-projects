from django.contrib import admin
from .models import Author, Audio


class AuthorAdmin(admin.ModelAdmin):
    list_per_page = 12
    list_display = ('image_tag', 'name', 'musics_count')


class AudioAdmin(admin.ModelAdmin):
    list_per_page = 12
    list_filter = ('author',)
    list_display = ('image_tag', 'title', 'author_name', 'played_count')


admin.site.register(Audio, AudioAdmin)
admin.site.register(Author, AuthorAdmin)
