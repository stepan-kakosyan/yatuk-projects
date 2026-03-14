from users import views
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_user, name='register'),
    path('profile/', views.profile, name='profile'),
    path('user-edit/', views.user_edit, name='user_edit'),
    path('addresses/', views.address_list, name='address_list'),
    path('address/add/', views.edit_address, name='add_address'),
    path('address/edit/<int:id>/', views.edit_address, name='edit_address'),
    path('address/remove/<int:id>/', views.remove_address, name='remove_address'),
    path('upload-profile-image/', views.upload_profile_image, name='upload_profile_image'),
]
