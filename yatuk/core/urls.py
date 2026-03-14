from core import views
from django.urls import path


urlpatterns = [
    path('', views.index, name="index"),
    path('reviews', views.reviews, name="reviews"),
    path('store', views.store, name="store"),
    path('store/<slug:category>/', views.store, name="store_category"),
    path('shipping', views.shipping, name="shipping"),
    path('cart', views.cart, name="cart"),
    path('contact-us', views.contact_us, name="contact_us"),
    path('product/<slug:slug>/', views.product_detail, name="product_detail"),
    path('set-language/', views.set_language, name="set_language"),
    path('set-theme/', views.set_theme, name="set_theme"),
    path('add-in-cart/<int:id>/', views.add_in_cart, name="add_in_cart"),
    path('get-cart-content/', views.get_cart_content, name="get_cart_content"),
    path('get-cart-count/', views.get_cart_count, name="get_cart_count"),
    path('remove-from-cart/<int:id>/', views.remove_from_cart, name="remove_from_cart"),
    path('change-item-count/<int:id>/', views.change_item_count, name="change_item_count"),
    path('get-cart-big/', views.get_cart_big, name="get_cart_big"),
    path('checkout/', views.checkout, name="checkout"),
    path('get-total-sum/', views.get_total_sum, name="get_total_sum"),
    path('order-result/', views.order_result, name="order_result"),
    path('change-address-form/', views.change_address_form, name="change_address_form"),
    path('change-shipping-method/', views.change_shipping_method, name="change_shipping_method"),
    path('privacy-policy/', views.privacy_policy, name="privacy_policy"),
    path('terms-and-conditions/', views.terms_and_conditions, name="terms_and_conditions"),
    path('cancel-order/', views.cancel_order, name="cancel_order"),
    path('author/<slug:slug>/', views.author, name="author"),
    path('authors/', views.authors, name="authors"),
    path('send_email_test/', views.send_email_test, name="send_email_test"),
]
