from baton.autodiscover import admin
from django.urls import path
from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import TemplateView
from .sitemaps import AudioSitemap
from django.contrib.sitemaps import views

sitemaps = {
    AudioSitemap.name: AudioSitemap
}

urlpatterns = i18n_patterns(
    path('', include('core_play.urls')),
    path('blog/', include('blog.urls')),
    path('admin/', admin.site.urls),
        path('sitemap.xml', views.sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('translate/', include('rosetta.urls'))
    ]
urlpatterns += [
    path('robots.txt', TemplateView.as_view(template_name='core/robots.txt', content_type='text/plain')),
]
