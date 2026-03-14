from django.urls import path
from . import views

urlpatterns = [
    path('transaction', views.transactions, name="transactions"),
    path('add-transaction', views.add_transaction, name="add_transaction"),
    path('products', views.products, name="products"),
    path('product/<int:pk>/', views.product, name="product"),

    path('add-cost', views.add_cost, name="add_cost"),
    path('costs', views.costs, name="costs"),
    path('add-transfer', views.add_transfer, name="add_transfer"),
    path('transfers', views.transfers, name="transfers"),
    path('collabarators', views.collabarators, name="collabarators"),
    path('change_filenames', views.change_filenames, name="change_filenames"),
]
