from django.db import models
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from utils.functions import unique_slug_generator, unique_armenian_slug_generator
from django.utils.safestring import mark_safe
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from django.core.files.base import ContentFile
from PIL import Image as IMG
from io import BytesIO
from core_game.models import Game, POSITION_CHOICES
from tinymce.models import HTMLField
from transliterate import translit
from users.models import User
from core_game.models import Author as Painter
from core_play.models import Author as Composer


class Genre(models.Model):
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name_hy


class Author(models.Model):
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    dates = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='authors/')
    signature = models.ImageField(upload_to='authors/', null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    optimized = models.ImageField(upload_to="media/product/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to="media/product/middle_optimized",
                                         verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,
                                  upload_to='media/product/thumb/', verbose_name=_("Thumbnail"))

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self)
        if self.image:
            imageTemproary = Image.open(self.image)
            outputIoStream = BytesIO()
            try:
                imageTemproary.save(outputIoStream, format='JPEG', quality=100)
                outputIoStream.seek(0)
                name = "%s.jpg" % self.slug
                self.image = InMemoryUploadedFile(outputIoStream, 'ImageField', name,
                                                  'image/jpeg', sys.getsizeof(outputIoStream), None)
            except Exception:
                pass

        try:
            self.thumbnail.save(
                **self.handleResize()
            )
        except Exception:
            self.thumbnail = self.image
        try:
            self.optimized.save(
                **self.handleOptimizedResize()
            )
        except Exception:
            self.optimized = self.image
        try:
            self.middle_optimized.save(
                **self.handleMiddleOptimizedResize()
            )
        except Exception:
            self.middle_optimized = self.image
        super(Author, self).save(*args, **kwargs)

    def __str__(self):
        return self.name_hy

    def image_tag(self):
        return mark_safe('<img style="width:60px;height:60px;object-fit:cover" src="'+"/media/"+str(self.signature)+'" />')

    @property
    def name(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def poem_count(self):
        return self.poems.count()

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


class AuthorBio(models.Model):
    author = models.OneToOneField(Author, blank=False, null=False, related_name='bio', on_delete=models.CASCADE)
    bio_hy = HTMLField(null=True, blank=True)
    bio_en = HTMLField(null=True, blank=True)
    bio_ru = HTMLField(null=True, blank=True)

    def __str__(self):
        return f"{self.author.name_hy} Bio"


class AuthorQuote(models.Model):
    author = models.OneToOneField(Author, blank=False, null=False, related_name='quotes', on_delete=models.CASCADE)
    bio_hy = HTMLField(null=True, blank=True)
    bio_en = HTMLField(null=True, blank=True)
    bio_ru = HTMLField(null=True, blank=True)

    def __str__(self):
        return f"{self.author.name_hy} Quotes"


class Poem(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=False, blank=False, related_name="poems")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=False, blank=False, related_name="poems")
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True, related_name="poems")
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=True, blank=True)
    name_ru = models.CharField(max_length=255, null=True, blank=True)
    content_hy = HTMLField(null=True, blank=True)
    content_en = HTMLField(null=True, blank=True)
    content_ru = HTMLField(null=True, blank=True)
    view_count = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_armenian_slug_generator(self, text=translit(self.name_hy, 'hy', reversed=True))
        super(Poem, self).save(*args, **kwargs)

    @property
    def name(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def author_name(self):
        return getattr(self.author, f"name_{get_language()}")

    def __str__(self):
        return self.author.name_hy + " - " + self.name_hy

    def image_tag(self):
        return mark_safe('<img style="width:60px;height:60px;object-fit:cover; border-radius: 50%;" src="' +
                         "/media/"+str(self.game.thumbnail)+'" />')


class PoemSection(models.Model):
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, null=False, blank=False, related_name="sections")
    order = models.IntegerField(default=2, null=False, blank=False)
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=True, blank=True)
    name_ru = models.CharField(max_length=255, null=True, blank=True)
    content_hy = HTMLField(null=True, blank=True)
    content_en = HTMLField(null=True, blank=True)
    content_ru = HTMLField(null=True, blank=True)

    def __str__(self):
        return self.poem.name_hy + " - " + self.name_hy


class Label(models.Model):
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name_hy


class PoemLabel(models.Model):
    label = models.ForeignKey(Label, on_delete=models.CASCADE, null=False, blank=False, related_name="poems")
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, null=False, blank=False, related_name="labels")


class Like(models.Model):
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, null=True, blank=True, related_name="likes")
    game = models.ForeignKey("core_game.Game", on_delete=models.CASCADE, null=True, blank=True, related_name="likes")
    audio = models.ForeignKey("core_play.Audio", on_delete=models.CASCADE, null=True, blank=True, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, null=True, blank=True, related_name="favorites")
    game = models.ForeignKey("core_game.Game", on_delete=models.CASCADE, null=True, blank=True, related_name="favorites")
    audio = models.ForeignKey("core_play.Audio", on_delete=models.CASCADE, null=True, blank=True, related_name="favorites")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="favorites")
    created_at = models.DateTimeField(auto_now_add=True)


class WantToRead(models.Model):
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, null=False, blank=False, related_name="want_to_reads")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="want_to_reads")
    created_at = models.DateTimeField(auto_now_add=True)


class PoemComment(models.Model):
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, null=True, blank=True, related_name="comments")
    game = models.ForeignKey("core_game.Game", on_delete=models.CASCADE, null=True, blank=True, related_name="comments")
    audio = models.ForeignKey("core_play.Audio", on_delete=models.CASCADE, null=True, blank=True, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="comments")
    text = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Photo(models.Model):
    name = models.CharField(max_length=500, null=False, blank=False)
    slug = models.SlugField(unique=False, null=False, blank=True)
    image = models.ImageField(upload_to='photo/')
    created_at = models.DateTimeField(auto_now_add=True)
    background_position = models.CharField(choices=POSITION_CHOICES, max_length=255, default="center", blank=False)
    optimized = models.ImageField(upload_to="media/photo/optimized",
                                  verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to="media/photo/middle_optimized",
                                         verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,
                                  upload_to='media/photo/thumb/', verbose_name=_("Thumbnail"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_armenian_slug_generator(self, text=translit(self.name, 'hy', reversed=True))
        if self.image:
            try:
                imageTemproary = Image.open(self.image)
                outputIoStream = BytesIO()
                imageTemproary.save(outputIoStream, format='JPEG', quality=100)
                outputIoStream.seek(0)
                name = "%s.jpg" % self.slug
                self.image = InMemoryUploadedFile(outputIoStream, 'ImageField', name,
                                                  'image/jpeg', sys.getsizeof(outputIoStream), None)
            except Exception:
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
        super(Photo, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def image_tag(self):
        return mark_safe('<img style="width:60px;height:60px;object-fit:cover; border-radius: 50%;" src="' +
                         "/media/"+str(self.thumbnail)+'" />')

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


class PhotoPerson(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=False, blank=False, related_name="photos")
    writer = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True, related_name="photos")
    composer = models.ForeignKey(Composer, on_delete=models.CASCADE, null=True, blank=True, related_name="photos")
    painter = models.ForeignKey(Painter, on_delete=models.CASCADE, null=True, blank=True, related_name="photos")
    text = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
