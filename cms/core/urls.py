from django.conf.urls import include, url
from core import views
from product.views import products
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name="index"),
    path('', include('product.urls'), name="products"),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add_todo', views.add_todo, name="add_todo"),
    path('done_undone_todo/<int:pk>/', views.done_undone_todo, name="done_undone_todo"),
    path('remove_todo/<int:pk>/', views.remove_todo, name="remove_todo"),
    path('todos', views.todos, name="todos"),
    path('set-language/', views.set_language, name="set_language"),
    path('status-order', views.status_order, name="status_order"),
    path('orders', views.orders, name="orders"),
    path('contact-us-list', views.contact_us_list, name="contact_us_list"),
    path('check-contact-us', views.check_contact_us, name="check_contact_us"),
]

