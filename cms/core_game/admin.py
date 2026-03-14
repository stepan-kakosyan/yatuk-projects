from django.contrib import admin
from django import forms
from .models import *


class AuthorAdmin(admin.ModelAdmin):
    list_per_page = 12
    list_display = ('image_tag', 'name', 'game_count')


class GameAdmin(admin.ModelAdmin):
    list_per_page = 12
    list_filter = ('author',)
    list_display = ('image_tag', 'name', 'author_name', 'played_count')
    fields = ('author', 'image', 'name_hy', 'name_ru', 'name_en', 'pid', 'background_position')

    def get_changeform_initial_data(self, request):
        return {
            'author': Author.objects.all().order_by('-id').first(),
            }

admin.site.register(Game, GameAdmin)
admin.site.register(Author, AuthorAdmin)

class BlogItemInline(admin.TabularInline):
      model = BlogItem
      extra = 0

class CanvasBlogAdmin(admin.ModelAdmin):
    list_per_page = 12
    list_display = ('image_tag', 'name', 'seen_count')
    inlines = (BlogItemInline,)

admin.site.register(CanvasBlog, CanvasBlogAdmin)
