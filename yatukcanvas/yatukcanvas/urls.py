from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import TemplateView
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, AuthorSitemap, PhotoSitemap, GameSitemap
import core.views as core_views
sitemaps = {
    "static": StaticViewSitemap,
    "author": AuthorSitemap,
    "photo": PhotoSitemap,
    'game': GameSitemap
}
urlpatterns = i18n_patterns(
    re_path(r'^', include('core.urls')),
    re_path(r'^', include('users.urls')),
    path('blog/', include('blog.urls')),
    re_path(r'^$', core_views.index, name="index"),
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
