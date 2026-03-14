from django.contrib import admin
from django import forms
from .models import *

class ProductGameInline(admin.TabularInline):
      model = ProductGame
      extra = 0
      list_display = ('game',)
      fields = list_display

class ProductAuthorInline(admin.TabularInline):
      model = ProductAuthor
      extra = 0
      list_display = ('author',)
      fields = list_display

class ProductImagesInline(admin.TabularInline):
      model = ProductImage
      extra = 0
      list_display = ('image_tag','image', 'middle_optimized', 'is_main', "for_share")
      fields = list_display
      readonly_fields = ('image_tag',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_tag','title', 'price')

    inlines = (ProductImagesInline, ProductAuthorInline, ProductGameInline)
    
class SketchAdmin(admin.ModelAdmin):
    list_display = ('image_tag',)

    
admin.site.register(ProductCategory)
admin.site.register(Product,ProductAdmin)
admin.site.register(Collaborator)
admin.site.register(SketchImage, SketchAdmin)