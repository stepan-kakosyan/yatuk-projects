from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from core.models import PoemAuthor, Photo, Poem


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
        return PoemAuthor.objects.filter(poems__isnull=False).distinct().order_by('id')

    def location(self,obj):
        return reverse('author', args=[obj.slug, "all"])

class PhotoSitemap(Sitemap):
    name = 'photo'
    changefreq = 'hourly'
    priority = 1
    limit = 50000

    def items(self):
        return Photo.objects.all()

    def location(self,obj):
        return reverse('photo', args=[obj.slug, obj.id])


class PoemSitemap(Sitemap):
    name = 'poem'
    changefreq = 'hourly'
    priority = 1
    limit = 50000

    def items(self):
        return Poem.objects.all()

    def location(self,obj):
        return reverse('poem', args=[obj.author.slug, obj.slug, obj.id])
