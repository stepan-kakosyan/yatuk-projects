from django.contrib import admin
from .models import *


class GameInline(admin.TabularInline):
      model = Game
      extra = 1
      list_display = ('iframe', 'piece_count')
      fields = list_display

class GameImageAdmin(admin.ModelAdmin):
    list_display = ('image_tag','title', 'author')

    inlines = (GameInline,)
    
admin.site.register(GameImage, GameImageAdmin)
