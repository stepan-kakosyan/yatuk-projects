from django.contrib import admin
from .models import *


class PoemAdmin(admin.ModelAdmin):
    list_per_page = 12
    list_display = ('name_hy', 'author_name')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(content_hy__icontains="<a")
admin.site.register(Poem, PoemAdmin)
