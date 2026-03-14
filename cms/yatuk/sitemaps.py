from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from core.models import Product, Author


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "hourly"

    def items(self):
        return ["index", "store", "shipping", "authors", "contact_us", "privacy_policy", "terms_and_conditions"]

    def location(self, item):
        return reverse(item)

class ProductSitemap(Sitemap):
    name = 'product'
    changefreq = 'hourly'
    priority = 1
    limit = 50000

    def items(self):
        return Product.objects.order_by('id')

    def location(self,obj):
        return f'/product/{obj.slug_en}/'

class AuthorSitemap(Sitemap):
    name = 'author'
    changefreq = 'hourly'
    priority = 1
    limit = 50000

    def items(self):
        return Author.objects.filter(authors__isnull=False).distinct().order_by('id')

    def location(self,obj):
        return f'/author/{obj.slug}/'
