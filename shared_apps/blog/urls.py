from django.urls import path

from .views import PostDetailView
from .views import PostListView
from .views import upload_image


app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='list'),
    path('upload-image/', upload_image, name='upload-image'),
    path('<slug:slug>/', PostDetailView.as_view(), name='detail'),
]
