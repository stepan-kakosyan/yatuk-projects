from django.contrib import admin
from .models import *
from django.forms import TextInput, Textarea


class AuthorAdmin(admin.ModelAdmin):
    list_per_page = 12
    list_display = ('image_tag', 'name')


class PoemSectionAdmin(admin.ModelAdmin):
    fields = ('poem','order', 'name_hy', 'content_hy',)
    list_display = ('poem', 'name_hy')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "poem":
            kwargs["queryset"] = Poem.objects.all().order_by("-id")
        return super(PoemSectionAdmin,self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_changeform_initial_data(self, request):
        return {
            'poem': Poem.objects.all().order_by('-id').first(),
            }

class PoemAdmin(admin.ModelAdmin):
    list_per_page = 12
    list_filter = ('author', )
    fields = ('genre', 'author', 'game', 'name_hy', 'content_hy')
    list_display = ('image_tag', 'name', 'author_name', 'view_count')

    def get_changeform_initial_data(self, request):
        return {
            'genre': Genre.objects.all().order_by('id').first(),
            'author': Author.objects.all().order_by('-id').first(),
            }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            kwargs["queryset"] = Author.objects.all().order_by("-id")
        return super(PoemAdmin,self).formfield_for_foreignkey(db_field, request, **kwargs)

class PhotoPersonInline(admin.TabularInline):
      model = PhotoPerson
      extra = 0
      list_display = ('writer', 'painter', 'composer')
      fields = list_display

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('name', )
    inlines = (PhotoPersonInline,)
    
class PoemCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'poem', 'game', 'audio', )


admin.site.register(PoemSection, PoemSectionAdmin)
admin.site.register(Photo, PhotoAdmin)

admin.site.register(Poem, PoemAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(Label)

admin.site.register(AuthorBio)
admin.site.register(AuthorQuote)
admin.site.register(PoemComment, PoemCommentAdmin)

