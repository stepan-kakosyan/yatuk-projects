from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.translation import check_for_language
from django.http import HttpResponseRedirect
from .models import (Product, ProductCategory, Slider, ShoppingCart, ShippingMethod,
                     Order, OrderItem, ProductTransaction, Game, Author, Review)
from .forms import ContactUsForm, OrderForm, AddressForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from functools import wraps
from django.shortcuts import resolve_url
from django.http import HttpResponse
import requests
from django.utils.translation import get_language
from yatuk.settings import BANK_PASSWORD, BANK_URL, BANK_USERNAME, BANK_CLIENT_ID
from users.models import Address
from django.template.loader import render_to_string
from utils.functions import send_yatuk_email
from datetime import datetime
from django.utils.translation import activate


def my_login_required(function=None, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        print("hosh")
        print(request.user.is_authenticated)
        if not request.user.is_authenticated and request.htmx:
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            return HttpResponse(status=204, headers={'HX-Redirect': resolved_login_url})
        return login_required(
            function=function,
            login_url=login_url,
            redirect_field_name=redirect_field_name
        )(request, *args, **kwargs)
    return wrapper


def set_language(request):
    lang_code = request.GET.get('language', settings.LANGUAGE_CODE)
    next_url = request.GET.get('next_url', f"/{lang_code}/")
    next_url = next_url.replace(f"/{get_language()}/", f"/{lang_code}/")
    response = HttpResponseRedirect(next_url)
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['language'] = lang_code
        response.set_cookie("django_language", lang_code, max_age=31536000)
        request.session.set_expiry(31536000)
        activate(lang_code)
    return response


def index(request):
    ctx = {
        "active": "index",
        "sliders": Slider.objects.all().order_by("?"),
        "products": Product.objects.all().order_by("?")[:4],
        "form": ContactUsForm(),
        "authors": Author.objects.filter(authors__isnull=False).distinct()
    }
    return render(request, 'core/index.html', context=ctx)


def authors(request):
    ctx = {
        "active": "authors",
        "authors": Author.objects.filter(authors__isnull=False).distinct()
    }
    return render(request, 'core/authors.html', context=ctx)


def reviews(request):
    ctx = {
        "active": "reviews",
        "reviews": Review.objects.filter(is_active=True).order_by("-date")
    }
    return render(request, 'core/reviews.html', context=ctx)


def contact_us(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            form.save()
            html_content = render_to_string('emails/contact-us.html', {'contact_details': cd})
            send_yatuk_email(subject=f"Կապ մեզ հետ՝ {cd['name']}",
                             message=f"Կապ մեզ հետ՝ {cd['name']}",
                             to_=["contact@yatuk.am", "stepankakosyan22@gmail.com"],
                             from_="info@yatuk.am",
                             html=html_content)
            messages.success(request, _('Your message was successfully sent.'))
            return render(request, 'core/partials/contact-form.html', {"form": ContactUsForm})
    else:
        form = ContactUsForm()
    ctx = {
        "active": "contact_us",
        'form': form
    }
    if request.htmx:
        return render(request, 'core/partials/contact-form.html', ctx)
    return render(request, 'core/contact-us.html', ctx)


def store(request, category=None):
    if category:
        products = Product.objects.filter(category__slug_en=category)
    else:
        products = Product.objects.all()
    ctx = {
        "products": products.order_by("?"),
        "categories": ProductCategory.objects.filter(products__isnull=False).distinct(),
        "active": "store",
        "selected_category": category if category else ""
    }
    if request.htmx:
        return render(request, 'core/partials/product-list.html', context=ctx)
    return render(request, 'core/store.html', context=ctx)


def product_detail(request, slug):
    product = Product.objects.get(slug_en=slug)
    ctx = {
        "product": product,
        "active": "store",
        "games": Game.objects.filter(games__product_id=product.id).distinct(),
        "products": Product.objects.filter(category=product.category).exclude(id=product.id).order_by("?")[:4],
    }
    return render(request, 'core/product-detail.html', context=ctx)


def author(request, slug):
    author = Author.objects.get(slug=slug)
    ctx = {
        "author": author,
        "games": Game.objects.filter(author=author)[:15],
        "products": Product.objects.filter(product_authors__author=author).distinct()
    }
    return render(request, 'core/author.html', context=ctx)


def shipping(request):
    ctx = {
        "active": "shipping",
        "methods": ShippingMethod.objects.all()
    }
    return render(request, 'core/shipping.html', context=ctx)


def set_theme(request):
    theme = request.GET.get('theme', "light")
    if hasattr(request, 'session'):
        request.session['theme'] = theme
    request.session.set_expiry(75686400)
    if request.user.is_authenticated:
        request.user.background = theme
        request.user.save()
    return HttpResponse("")


@my_login_required
def add_in_cart(request, id):
    product = Product.objects.get(id=id)
    product_in_cart = ShoppingCart.objects.filter(user=request.user, product=product)
    if product_in_cart.exists():
        item = product_in_cart.first()
        item.count = item.count + 1
        item.save()
    else:
        ShoppingCart.objects.create(user=request.user, product=product)
    response = HttpResponse("<i class='fa fa-check'></i>")
    response['HX-Trigger-After-Swap'] = "cart-changed"
    return response


def get_cart_content(request):
    return render(request, 'partials/cart-content.html')


def get_cart_count(request):
    return render(request, 'partials/cart-number.html')


@my_login_required
def remove_from_cart(request, id):
    ShoppingCart.objects.get(id=id).delete()
    response = HttpResponse("")
    response['HX-Trigger-After-Swap'] = "cart-changed"
    return response


@my_login_required
def cart(request):
    return render(request, 'core/cart.html')


@my_login_required
def change_item_count(request, id):
    count = int(request.GET.get("count"))
    item = ShoppingCart.objects.get(id=id)
    if count == 1:
        item.count = item.count+1
        item.save()
    else:
        if item.count == 1:
            item.delete()
        else:
            item.count = item.count - 1
            item.save()
    response = HttpResponse("")
    response['HX-Trigger-After-Swap'] = "cart-changed"
    return response


@my_login_required
def get_cart_big(request):
    return render(request, "core/partials/shopping-cart-page.html")


@my_login_required
def checkout(request):
    if request.user.cart_products.all().exists():
        addresses = Address.objects.filter(user=request.user)
        if request.method == "POST":
            form = OrderForm(request.POST, user=request.user)
            address_form = AddressForm(request.POST)
            if form.is_valid() and address_form.is_valid():
                cd = form.cleaned_data
                address_form_cd = address_form.cleaned_data
                if cd['old_address']:
                    address = Address.objects.get(id=cd['old_address'].id)
                else:
                    address = Address(user=request.user)
                address.state = address_form_cd['state']
                address.city = address_form_cd['city']
                address.address = address_form_cd['address']
                address.postal_code = address_form_cd['postal_code']
                address.save()
                order = Order(
                    user=request.user,
                    address=address,
                    comment=cd['comment'],
                    shipping_method=cd['shipping_method'],
                    phone_number=cd['phone_number'],
                    shipping_price=cd['shipping_method'].price,
                    amount=1,
                    status="not_paid"
                )
                order.save()
                amount = cd['shipping_method'].price
                for item in request.user.cart_products.all():
                    price = item.product.price*item.count
                    OrderItem.objects.create(
                        quantity=item.count,
                        product=item.product,
                        price=price,
                        order=order
                    )
                    amount += price
                order.amount = amount
                order.save()
                json_data = {
                    "ClientID": BANK_CLIENT_ID,
                    "Amount": order.amount,
                    "OrderID": int(order.id) + 2548150,
                    "Username": BANK_USERNAME,
                    "Password": BANK_PASSWORD,
                    "BackURL": f"{ request.scheme }://{ request.META['HTTP_HOST'] }/order-result?order_id={order.id}",
                    "Description": f"ORDER #{order.id}"
                }
                req = requests.post(f"{BANK_URL}/api/VPOS/InitPayment", json=json_data)
                paymentID = req.json()['PaymentID']
                order.payment_id = paymentID
                order.save()
                redirect_url = f"{BANK_URL}/Payments/Pay?id={paymentID}&lang={get_language()}"
                return HttpResponse(status=204, headers={'HX-Redirect': redirect_url})
            if 'shipping_method' in request.POST and request.POST['shipping_method'] is not None and \
                    request.POST['shipping_method'] != "":
                shipping_method = ShippingMethod.objects.get(id=request.POST['shipping_method'])
                shipping_price = shipping_method.price
            else:
                shipping_method = ShippingMethod.objects.all().first().id
                shipping_price = 0
            if "state" in request.POST and request.POST['state'] is not None and request.POST['state'] != "":
                shipping_methods = ShippingMethod.objects.filter(states_available__in=[request.POST['state']])
            else:
                shipping_methods = ShippingMethod.objects.all()
            return render(request, 'core/partials/checkout-form.html', {
                    "form": form,
                    "address_form": address_form,
                    "show_address": addresses.count() > 1,
                    "addresses": addresses,
                    "selected_method": shipping_method.id,
                    "shipping_price": shipping_price,
                    "shipping_methods": shipping_methods
                })
        else:
            shipping_methods = ShippingMethod.objects.all()
            ctx = {
                "form": OrderForm(user=request.user),
                "show_address": addresses.count() > 1,
                "address_form": AddressForm(),
                "addresses": addresses,
                "shipping_methods": shipping_methods,
                "shipping_price": shipping_methods.first().price,
                "selected_method": shipping_methods.first().id
            }
            return render(request, 'core/checkout.html', context=ctx)
    else:
        return redirect(reverse_lazy("index"))


@my_login_required
def order_result(request):
    order_id = request.GET.get("order_id", None)
    if order_id:
        order = Order.objects.get(id=order_id)
        if order.payment_id:
            if order.status != "accepted":
                if request.user != order.user:
                    return redirect(reverse_lazy("index"))
                json_data = {
                    "PaymentID": order.payment_id,
                    "Username": BANK_USERNAME,
                    "Password": BANK_PASSWORD,
                }
                req = requests.post(f"{BANK_URL}/api/VPOS/GetPaymentDetails", json=json_data)
                if req.json()['ResponseCode'] == "00":
                    status = "succeed"
                    order.status = "accepted"
                    order.save()
                    request.user.cart_products.all().delete()
                    for i in order.items.all():
                        pt = ProductTransaction(
                            count=i.quantity,
                            product=i.product,
                            amount=i.price,
                            type="website",
                            date=datetime.today(),
                            order=order
                        )
                        pt.save()
                    send_order_email(order_id=order.id, succeed=True)
                else:
                    send_order_email(order_id=order.id, succeed=False)
                    status = "failed"
            else:
                status = "suceed"
            ctx = {
                "status": status,
                "order": order
            }
            return render(request, "core/order-result.html", context=ctx)
        else:
            send_order_email(order_id=order.id, succeed=False)
            ctx = {
                "status": "failed"
            }
            return render(request, "core/order-result.html", context=ctx)
    else:
        ctx = {
            "status": "failed"
        }
        send_order_email(order_id=order.id, succeed=False)
        return render(request, "core/partials/order_result.html", context=ctx)


def change_address_form(request):
    address_form = AddressForm(instance=Address.objects.get(id=request.GET.get('old_address')))
    response = render(request, "core/partials/address-form.html", context={"address_form": address_form})
    response['HX-Trigger-After-Swap'] = "state-changed"
    return response


def change_shipping_method(request):
    state = request.GET.get('state')
    shipping_methods = ShippingMethod.objects.filter(states_available__in=[state])
    selected_method = shipping_methods.first().id
    response = render(request, "core/partials/shipping-method-radio.html", context={
                        "selected_method": selected_method,
                        "shipping_methods": shipping_methods,
                        })
    response['HX-Trigger-After-Swap'] = "shipping-method-changed"
    return response


def get_total_sum(request):
    shipping_method = request.GET.get('shipping_method')
    shipping_method = ShippingMethod.objects.get(id=shipping_method)
    return render(request, "core/partials/total-sum.html", context={
                        "shipping_price": shipping_method.price,
                        })


def send_order_email(order_id, succeed):
    order = Order.objects.get(id=order_id)
    if succeed:
        ProductTransaction.objects.filter(order=order).delete()
        html_content = render_to_string('emails/new-order.html', {'order': order})
        send_yatuk_email(subject=f"Նոր պատվեր՝ {order.id}",
                         message=f"Նոր պատվեր՝ {order.id}",
                         to_=["info@yatuk.am", "stepankakosyan22@gmail.com"],
                         from_="info@yatuk.am",
                         html=html_content)
    else:
        html_content = render_to_string('emails/failed-order.html', {'order': order})
        send_yatuk_email(subject=f"Ձախողված պատվեր՝ {order.id}",
                         message=f"Ձախողված պատվեր՝ {order.id}",
                         to_=["info@yatuk.am", "stepankakosyan22@gmail.com"],
                         from_="info@yatuk.am",
                         html=html_content)
    return True


def privacy_policy(request):
    return render(request, 'core/privacy-policy.html')


def terms_and_conditions(request):
    return render(request, 'core/terms-and-conditions.html')


@my_login_required
def cancel_order(request):
    order_id = request.GET.get("order_id")
    if order_id:
        order = Order.objects.get(id=order_id)
        if (order.user != request.user) or (order.status not in ["in_process", "accepted"]):
            return redirect(reverse_lazy("index"))
        json_data = {
            "PaymentID": order.payment_id,
            "Amount": order.amount,
            "Username": BANK_USERNAME,
            "Password": BANK_PASSWORD,
        }
        req = requests.post(f"{BANK_URL}/api/VPOS/RefundPayment", json=json_data)
        if req.json()['ResponseCode'] == "00":
            order.status = "cancelled"
            order.save()
            status = "succeed"

            html_content = render_to_string('emails/cancelled-order.html', {'order': order})
            send_yatuk_email(subject=f"Չեղարկված պատվեր՝ {order.id}",
                             message=f"Չեղարկված պատվեր՝ {order.id}",
                             to_=["contact@yatuk.am", "stepankakosyan22@gmail.com"],
                             from_="info@yatuk.am",
                             html=html_content)
        else:
            status = "failed"
        return render(request, "users/partials/order-card.html",
                      context={
                            "status": status,
                            "list_changed": True,
                            "order": order
                        })
    return redirect(reverse_lazy("index"))


def send_email_test(request):
    order = Order.objects.get(id=59)
    html_content = render_to_string('emails/cancelled-order.html', {'order': order})
    email = send_yatuk_email(subject=f"Չեղարկված պատվեր՝ {order.id}",
                             message=f"Չեղարկված պատվեր՝ {order.id}",
                             to_=["contact@yatuk.am", "stepankakosyan22@gmail.com"],
                             from_="info@yatuk.am",
                             html=html_content)
    return HttpResponse(str(email))
