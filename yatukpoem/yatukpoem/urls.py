from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import TemplateView
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, AuthorSitemap, PhotoSitemap, PoemSitemap
from django.urls import path

sitemaps = {
    "static": StaticViewSitemap,
    "author": AuthorSitemap,
    "photo": PhotoSitemap,
    'poem': PoemSitemap
}

urlpatterns = i18n_patterns(
    path('', include('core.urls')),
    path('', include('users.urls')),
    path('blog/', include('blog.urls')),
    path(
        "sitemap.xml", sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    )
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
