from django.contrib import admin
from django.urls import path
from django.conf.urls import include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.conf.urls.i18n import i18n_patterns


urlpatterns = i18n_patterns(
    path('', include('core.urls')),
    path('blog/', include('blog.urls')),
    
    path('admin/', admin.site.urls)
)
urlpatterns += [
    path('tinymce/', include('tinymce.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r'^translate/', include('rosetta.urls'))
    ]