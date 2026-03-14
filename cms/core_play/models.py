from django.db import models
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from utils.functions import unique_slug_generator
from django.utils.safestring import mark_safe
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys, os
from django.core.files.base import ContentFile
from PIL import Image as IMG
from io import BytesIO


class Author(models.Model):
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)    
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    quote_hy = models.CharField(max_length=500, null=True, blank=True)
    quote_en = models.CharField(max_length=500, null=True, blank=True)    
    quote_ru = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='authors/')
    optimized = models.ImageField(upload_to = "media/authors/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to = "media/authors/middle_optimized", verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,upload_to ='media/authors/thumb/', verbose_name=_("Thumbnail"))

    slug = models.SlugField(unique=True, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_hy

    def image_tag(self):
        return mark_safe('<img style="width:60px;height:60px;object-fit:cover; border-radius: 50%;" src="'+"/media/"+str(self.image)+'" />')

    @property
    def name(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def quote(self):
        return getattr(self, f"quote_{get_language()}") if getattr(self, f"quote_{get_language()}") else ""
    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self)
        if self.image:
            imageTemproary = Image.open(self.image)
            outputIoStream = BytesIO()
            imageTemproary.save(outputIoStream , format='JPEG', quality=60)
            outputIoStream.seek(0)
            name = "%s.jpg" % self.slug
            self.image = InMemoryUploadedFile(outputIoStream,'ImageField', name, 
                                              'image/jpeg', sys.getsizeof(outputIoStream), None)
        self.thumbnail.save(
        **self.handleResize()
        )
        self.optimized.save(
        **self.handleOptimizedResize()
        )
        self.middle_optimized.save(
        **self.handleMiddleOptimizedResize()
        )
        super(Author, self).save(*args, **kwargs)

    def resizeImg(self, img_size):
        img: IMG.Image = IMG.open(self.image)
        img.thumbnail(img_size, IMG.ANTIALIAS)
        outputIO = BytesIO()
        img.save(outputIO, format=img.format, quality=100)
        return outputIO, img

    def handleResize(self):
        imgSize = (100, 150)
        imgName = self.slug
        outputIO, img = self.resizeImg(imgSize)
        return {
                'name': f'{imgName}.{img.format}',
                'content': ContentFile(outputIO.getvalue()),
                'save': False,
        }

    def handleOptimizedResize(self):
        imgSize = (500, 700)
        imgName = self.slug
        outputIO, img = self.resizeImg(imgSize)
        return {
            'name': f'{imgName}.{img.format}',
            'content': ContentFile(outputIO.getvalue()),
            'save': False,
        }
        
    def handleMiddleOptimizedResize(self):
        imgSize = (250, 350)
        imgName = self.slug
        outputIO, img = self.resizeImg(imgSize)
        return {
            'name': f'{imgName}.{img.format}',
            'content': ContentFile(outputIO.getvalue()),
            'save': False,
        }

    @property
    def musics_count(self):
        return self.musics.count()

class Audio(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=False, blank=False, related_name="musics")
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)    
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to='authors/')
    optimized = models.ImageField(upload_to = "media/authors/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to = "media/authors/middle_optimized", verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,upload_to ='media/authors/thumb/', verbose_name=_("Thumbnail"))
    audio = models.FileField(upload_to='audios/')
    played_count = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(unique=True, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self):
        if not self.pk:
            self.slug = unique_slug_generator(self)
        if self.image:
            imageTemproary = Image.open(self.image)
            outputIoStream = BytesIO()
            imageTemproary.save(outputIoStream , format='JPEG', quality=60)
            outputIoStream.seek(0)
            name = "%s.jpg" % self.slug
            self.image = InMemoryUploadedFile(outputIoStream,'ImageField', name, 
                                            'image/jpeg', sys.getsizeof(outputIoStream), None)
        self.thumbnail.save(
        **self.handleResize()
        )
        self.optimized.save(
        **self.handleOptimizedResize()
        )
        self.middle_optimized.save(
        **self.handleMiddleOptimizedResize()
        )
        return super().save()
    def resizeImg(self, img_size):
        img: IMG.Image = IMG.open(self.image)
        img.thumbnail(img_size, IMG.ANTIALIAS)
        outputIO = BytesIO()
        img.save(outputIO, format=img.format, quality=100)
        return outputIO, img

    def handleResize(self):
        imgSize = (100, 150)
        imgName = self.slug
        outputIO, img = self.resizeImg(imgSize)
        return {
            'name': f'{imgName}.{img.format}',
            'content': ContentFile(outputIO.getvalue()),
            'save': False,
            }

    def handleOptimizedResize(self):
        imgSize = (500, 700)
        imgName = self.slug
        outputIO, img = self.resizeImg(imgSize)
        return {
            'name': f'{imgName}.{img.format}',
            'content': ContentFile(outputIO.getvalue()),
            'save': False,
        }
        
    def handleMiddleOptimizedResize(self):
        imgSize = (250, 350)
        imgName = self.slug
        outputIO, img = self.resizeImg(imgSize)
        return {
            'name': f'{imgName}.{img.format}',
            'content': ContentFile(outputIO.getvalue()),
            'save': False,
        }

    @property
    def title(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def author_name(self):
        return getattr(self.author, f"name_{get_language()}")

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe('<img style="width:60px;height:60px;object-fit:cover; border-radius: 50%;" src="'+"/media/"+str(self.image)+'" />')
