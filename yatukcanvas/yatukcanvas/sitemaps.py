from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from core.models import GameAuthor, Photo, Game


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "hourly"

    def items(self):
        return ["index", "authors", "contact_us", "privacy_policy", "terms_and_conditions", "photos"]

    def location(self, item):
        return reverse(item)


class AuthorSitemap(Sitemap):
    name = 'author'
    changefreq = 'hourly'
    priority = 1
    limit = 50000

    def items(self):
        return GameAuthor.objects.filter(games__isnull=False).distinct().order_by('id')

    def location(self,obj):
        return reverse('author', args=[obj.slug])

class PhotoSitemap(Sitemap):
    name = 'photo'
    changefreq = 'hourly'
    priority = 1
    limit = 50000

    def items(self):
        return Photo.objects.all()

    def location(self,obj):
        return reverse('photo', args=[obj.slug, obj.id])


class GameSitemap(Sitemap):
    name = 'game'
    changefreq = 'hourly'
    priority = 1
    limit = 50000

    def items(self):
        return Game.objects.all()

    def location(self,obj):
        return reverse('game', args=[obj.author.slug, obj.slug, obj.id])
