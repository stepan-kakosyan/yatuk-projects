from django.db import models
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
import random
from utils.functions import compute_average_image_color, unique_slug_generator
from django.db import models
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys, os
from django.core.files.base import ContentFile
from PIL import Image as IMG
from io import BytesIO


POSITION_CHOICES = [
    ('top', 'Top'),
    ('center', 'Center'),
    ('bottom', 'Bottom')
]

class Author(models.Model):
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)    
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    bio_hy = models.TextField(null=True, blank=True)
    bio_en = models.TextField(null=True, blank=True)    
    bio_ru = models.TextField(null=True, blank=True)
    dates = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='authors/')
    slug = models.SlugField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    main_image = models.ImageField(upload_to='game/', blank=True, null=True)
    optimized = models.ImageField(upload_to = "media/product/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to = "media/product/middle_optimized", verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,upload_to ='media/product/thumb/', verbose_name=_("Thumbnail"))
    signature = models.ImageField(upload_to='authors/', null=True, blank=True)

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

    def __str__(self):
        return self.name_hy

    def image_tag(self):
        return mark_safe('<img style="width:60px;height:60px;object-fit:cover; border-radius: 50%;" src="'+"/media/"+str(self.main_image)+'" />')

    @property
    def name(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def game_count(self):
        return self.games.count()

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


class Game(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=False, blank=False, related_name="games")
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)    
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to='game/')
    main_color = models.CharField(max_length=255, null=True, blank=True)
    pid = models.CharField(max_length=255, null=False, blank=False)
    played_count = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(unique=True, null=False, blank=True)
    background_position = models.CharField(choices=POSITION_CHOICES, max_length=255, default="center", blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    optimized = models.ImageField(upload_to = "media/product/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to = "media/product/middle_optimized", verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,upload_to ='media/product/thumb/', verbose_name=_("Thumbnail"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self)
        if self.image:
            try:
                imageTemproary = Image.open(self.image)
                outputIoStream = BytesIO()
                imageTemproary.save(outputIoStream , format='JPEG', quality=60)
                outputIoStream.seek(0)
                name = "%s.jpg" % self.slug
                self.image = InMemoryUploadedFile(outputIoStream,'ImageField', name, 
                                                'image/jpeg', sys.getsizeof(outputIoStream), None)
                self.main_color = compute_average_image_color(self)
            except:
                self.main_color = "808080"
        self.thumbnail.save(
        **self.handleResize()
        )
        self.optimized.save(
        **self.handleOptimizedResize()
        )
        self.middle_optimized.save(
        **self.handleMiddleOptimizedResize()
        )
        super(Game, self).save(*args, **kwargs)

    @property
    def name(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def author_name(self):
        return getattr(self.author, f"name_{get_language()}")

    def __str__(self):
        return self.author.name_hy +" - " + self.name_hy

    def image_tag(self):
        return mark_safe('<img style="width:60px;height:60px;object-fit:cover; border-radius: 50%;" src="'+"/media/"+str(self.image)+'" />')

    @property
    def color(self):
        average_color = compute_average_image_color(self)
        return average_color

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



class CanvasBlog(models.Model):
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)    
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    short_hy = models.CharField(max_length=2000, null=False, blank=False)
    short_en = models.CharField(max_length=2000, null=False, blank=False)    
    short_ru = models.CharField(max_length=2000, null=False, blank=False)
    description_hy = models.TextField(null=True, blank=True)
    description_en = models.TextField(null=True, blank=True)    
    description_ru = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='game/')
    seen_count = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(unique=True, null=False, blank=True)
    optimized = models.ImageField(upload_to = "media/product/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to = "media/product/middle_optimized", verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,upload_to ='media/product/thumb/', verbose_name=_("Thumbnail"))
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self)
        if self.image:
            try:
                imageTemproary = Image.open(self.image)
                outputIoStream = BytesIO()
                imageTemproary.save(outputIoStream , format='JPEG', quality=60)
                outputIoStream.seek(0)
                name = "%s.jpg" % self.slug
                self.image = InMemoryUploadedFile(outputIoStream,'ImageField', name, 
                                                'image/jpeg', sys.getsizeof(outputIoStream), None)
            except:
                pass
        self.thumbnail.save(
        **self.handleResize()
        )
        self.optimized.save(
        **self.handleOptimizedResize()
        )
        self.middle_optimized.save(
        **self.handleMiddleOptimizedResize()
        )
        super(CanvasBlog, self).save(*args, **kwargs)

    @property
    def name(self):
        return getattr(self, f"name_{get_language()}")

    def __str__(self):
        return self.name

    def image_tag(self):
        return mark_safe('<img style="width:60px;height:60px;object-fit:cover; border-radius: 50%;" src="'+"/media/"+str(self.image)+'" />')

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


class BlogItem(models.Model):
    short_hy = models.CharField(max_length=2000, null=False, blank=False)
    short_en = models.CharField(max_length=2000, null=False, blank=False)    
    short_ru = models.CharField(max_length=2000, null=False, blank=False)
    blog = models.ForeignKey(CanvasBlog, on_delete=models.PROTECT, null=False, blank=False, 
                               related_name="blog_item")
    canvas = models.ForeignKey(Game, on_delete=models.PROTECT, null=False, blank=False, 
                               related_name="blog_item")

    def __str__(self):
        return self.canvas