from users import views
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_user, name='register'),
    path('profile/', views.profile, name='profile'),
    path('user-edit/', views.user_edit, name='user_edit'),
    path('upload-profile-image/', views.upload_profile_image, name='upload_profile_image'),
]
