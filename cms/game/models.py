from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _


class GameImage(models.Model):
    title_en = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title English"))
    title_ru = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Russian"))
    title_hy = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Armenian"))
    description_en = models.TextField(verbose_name=_("Description English"))
    description_ru = models.TextField(verbose_name=_("Description Russian"))
    description_hy = models.TextField(verbose_name=_("Description Armenian"))
    author_en = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Author English"))
    author_ru = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Author Russian"))
    author_hy = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Author Armenian"))
    image = models.ImageField(upload_to="media/gameimage", null=True, blank=True, verbose_name=_("Image"))

    def __str__(self):
        return self.title

    @property
    def title(self):
        return getattr(self, f"title_{get_language()}")

    @property
    def author(self):
        return getattr(self, f"author_{get_language()}")

    @property
    def description(self):
        return getattr(self, f"description_{get_language()}")

    def image_tag(self):
        return mark_safe('<img style="max-width:50px;max-height:75px;object-fit:contain" src="' +
                         "/media/"+str(self.image)+'" />')

    @property
    def all_games(self):
        return self.games.all().order_by("piece_count")


class Game(models.Model):
    image = models.ForeignKey(GameImage, related_name="games",
                              on_delete=models.CASCADE, null=False, blank=False)
    iframe = models.TextField()
    piece_count = models.PositiveIntegerField(default=35)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return str(self.piece_count)
