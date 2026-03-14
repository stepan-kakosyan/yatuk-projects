from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post
from core.models import Author
from core.models import Product


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "hourly"

    def items(self):
        return [
            "index",
            "store",
            "shipping",
            "authors",
            "contact_us",
            "privacy_policy",
            "terms_and_conditions",
        ]

    def location(self, item):
        return reverse(item)


class BlogListSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['blog:list']

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(Sitemap):
    name = 'blog_post'
    changefreq = 'daily'
    priority = 0.9
    limit = 50000

    def items(self):
        return Post.objects.published().order_by('-published_at', '-id')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('blog:detail', kwargs={'slug': obj.slug})


class ProductSitemap(Sitemap):
    name = 'product'
    changefreq = 'hourly'
    priority = 1
    limit = 50000

    def items(self):
        return Product.objects.order_by('id')

    def location(self, obj):
        return f'/product/{obj.slug_en}/'


class AuthorSitemap(Sitemap):
    name = 'author'
    changefreq = 'hourly'
    priority = 1
    limit = 50000

    def items(self):
        return Author.objects.filter(
            authors__isnull=False,
        ).distinct().order_by('id')

    def location(self, obj):
        return f'/author/{obj.slug}/'
