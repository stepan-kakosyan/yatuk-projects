from django.conf.urls import include, url
from users import views
from django.urls import path


urlpatterns = [
    # path('check-code/', views.check_code, name="check_code"),
]

htmx_url_patterns = [
    # path('full-name/', views.full_name, name="full_name"),
]

urlpatterns += htmx_url_patterns
