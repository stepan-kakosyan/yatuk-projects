from django.contrib.sitemaps import Sitemap

from core_play.models import Audio
from django.urls import reverse


class AudioSitemap(Sitemap):
    name = 'audio'
    changefreq = 'hourly'
    priority = 1
    limit = 50000

    def items(self):
        return Audio.objects.order_by('id')

    def location(self,obj):
        return reverse('index_song', kwargs={'author': obj.author.slug,'slug': obj.slug})
