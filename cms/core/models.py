from django.db import models
from users.models import User, State, Address
from django.utils.translation import gettext_lazy as _
from product.models import Product
from django.utils.text import slugify
from django.core.files.base import ContentFile
from PIL import Image as IMG
from io import BytesIO
from django.utils.translation import get_language
from django.utils.safestring import mark_safe


ORDER_STATUS = [
    ("not_paid", _("Not Paid")),
    ("accepted", _("Accepted")),
    ("in_process", _("In Process")),
    ("shipping", _("Shipping")),
    ("done", _("Done")),
    ("cancelled", _("Cancelled"))
]


class ToDo(models.Model):
    text = models.CharField(max_length=255, null=False, blank=False)
    owner = models.ForeignKey(User, null=False, blank=False,
                              related_name="todos", on_delete=models.CASCADE)
    done = models.BooleanField(default=False)
    removed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class ContactUs(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    email_or_phone = models.CharField(max_length=255, null=False, blank=False)
    text = models.TextField(max_length=2000, null=False, blank=False)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


class Slider(models.Model):
    title_en = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title English"))
    title_ru = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Russian"))
    title_hy = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Armenian"))
    description_en = models.TextField(verbose_name=_("Description English"))
    description_ru = models.TextField(verbose_name=_("Description Russian"))
    description_hy = models.TextField(verbose_name=_("Description Armenian"))
    ordering = models.PositiveSmallIntegerField(default=1)
    main_image = models.ImageField(upload_to="media/slider", verbose_name=_("Main Image"))
    blur_image = models.ImageField(upload_to="media/slider", verbose_name=_("Blur Image"))
    link = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.title_en}"

    def save(self, *args, **kwargs):
        self.main_image.save(
            **self.handleMainResize()
        )
        self.blur_image.save(
            **self.handleBlurResize()
        )
        super().save(*args, **kwargs)

    def handleMainResize(self):
        imgSize = (700, 700)
        imgName = slugify(self.title_en)
        outputIO, img = self.resizeMainImg(imgSize)
        return {
                'name': f'{imgName}.{img.format}',
                'content': ContentFile(outputIO.getvalue()),
                'save': False,
        }

    def handleBlurResize(self):
        imgSize = (700, 700)
        imgName = slugify(self.title_en)
        outputIO, img = self.resizeBlurImg(imgSize)
        return {
                'name': f'{imgName}.{img.format}',
                'content': ContentFile(outputIO.getvalue()),
                'save': False,
        }

    def resizeMainImg(self, img_size):
        img: IMG.Image = IMG.open(self.main_image)
        img.thumbnail(img_size, IMG.ANTIALIAS)
        outputIO = BytesIO()
        img.save(outputIO, format=img.format, quality=70)
        return outputIO, img

    def resizeBlurImg(self, img_size):
        img: IMG.Image = IMG.open(self.blur_image)
        img.thumbnail(img_size, IMG.ANTIALIAS)
        outputIO = BytesIO()
        img.save(outputIO, format=img.format, quality=70)
        return outputIO, img


class ShoppingCart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name="products", null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="cart_products", null=False, blank=False)
    count = models.PositiveIntegerField(null=False, blank=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)


class ShippingMethod(models.Model):
    title_en = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title English"))
    title_ru = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Russian"))
    title_hy = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Armenian"))
    description_en = models.TextField(verbose_name=_("Description English"))
    description_ru = models.TextField(verbose_name=_("Description Russian"))
    description_hy = models.TextField(verbose_name=_("Description Armenian"))
    image = models.ImageField(upload_to="media/slider", verbose_name=_("Main Image"))
    price = models.IntegerField(null=False, blank=False, verbose_name=_("Price"))
    states_available = models.ManyToManyField(State, related_name="states")

    def __str__(self):
        return getattr(self, f'title_{get_language()}')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.SET_NULL,
                                        related_name='orders',
                                        null=True, blank=True)
    shipping_price = models.IntegerField(null=True, blank=True, verbose_name=_("Shipping Price"))
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, related_name='orders',
                                null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_id = models.CharField(max_length=100, blank=True)
    shipping_number = models.CharField(max_length=100, blank=True, null=True)
    amount = models.PositiveIntegerField(null=False, blank=False, verbose_name=_("Amount"))
    status = models.CharField(choices=ORDER_STATUS, blank=False, null=False, max_length=255,
                              verbose_name=_("status"))
    comment = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'Order #{self.id}'

    @property
    def status_display(self):
        return list(filter(lambda x: x[0] == self.status, ORDER_STATUS))[0][1]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ordered_products")
    price = models.PositiveIntegerField(null=False, blank=False, verbose_name=_("Price"))
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product}'


class Review(models.Model):
    image = models.ImageField(upload_to='review/')
    name = models.CharField(max_length=255, null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    star = models.PositiveSmallIntegerField(default=5)
    date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    facebook_link = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def image_(self):
        return mark_safe('<img style="width:80px;height:80px;object-fit:cover;" src="'+"/media/"+str(self.image)+'" />')

    @property
    def link(self):
        return mark_safe(f'<a target="_blank" href="{self.facebook_link}"/>Link</a>')
