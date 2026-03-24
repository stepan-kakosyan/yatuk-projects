from django.db import models
from PIL import Image as IMG
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.safestring import mark_safe
from django.db.models import Sum, Q
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.utils.text import slugify
from core_game.models import Author, Game
from tinymce.models import HTMLField
from datetime import datetime
import time


TRANSACTION_TYPES = [
    ("website", _("Website")),
    ("facebook", _("Facebook")),
    ("collaborator", _("Collaborator")),
    ("gift", _("Gift")),
    ("other", _("Other"))
]
COLORS = [
    'rgba(255, 99, 132, 0.5)',
    'rgba(54, 162, 235, 0.5)',
    'rgba(255, 206, 86, 0.5)',
    'rgba(75, 192, 192, 0.5)',
    'rgba(153, 102, 255, 0.5)',
    'rgba(255, 159, 64, 0.5)'
]
BORDER_COLORS = [
            'rgba(255,99,132,1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)'
]
COST_TYPES = [
    ("direct", _("Direct")),
    ("indirect", _("Indirect")),
]


class ProductCategory(models.Model):
    title_en = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Title English"))
    title_ru = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Title Russian"))
    title_hy = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Title Armenian"))
    slug_en = models.CharField(max_length=255, null=True, blank=True)
    slug_ru = models.CharField(max_length=255, null=True, blank=True)
    slug_hy = models.CharField(max_length=255, null=True, blank=True)
    description_en = models.TextField(verbose_name=_("Description English"))
    description_ru = models.TextField(verbose_name=_("Description Russian"))
    description_hy = models.TextField(verbose_name=_("Description Armenian"))
    icon = models.ImageField(upload_to="media/icon", null=True, blank=True, verbose_name=_("Icon"))

    def __str__(self):
        return self.title

    @property
    def title(self):
        return getattr(self, f"title_{get_language()}")

    @property
    def description(self):
        return getattr(self, f"description_{get_language()}")

    def image_tag(self):
        return mark_safe('<img style="max-width:50px;max-height:75px;object-fit:contain" src="' +
                         "/media/"+str(self.icon)+'" />')


class Product(models.Model):
    title_en = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title English"))
    title_ru = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Russian"))
    title_hy = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Armenian"))
    slug_en = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Slug English"))
    slug_ru = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Slug Russian"))
    slug_hy = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Slug Armenian"))
    description_en = HTMLField(verbose_name=_("Description English"))
    description_ru = HTMLField(verbose_name=_("Description Russian"))
    description_hy = HTMLField(verbose_name=_("Description Armenian"))
    price = models.IntegerField(null=False, blank=False, verbose_name=_("Price"))
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, null=False,
                                 verbose_name=_("Category"), related_name="products")
    total_count = models.IntegerField(default=50, verbose_name=_("Total Count"))
    shop_url = models.CharField(null=True, blank=True, max_length=255)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"{self.category.title} - {self.title}"

    @property
    def title(self):
        return getattr(self, f"title_{get_language()}")

    @property
    def description(self):
        return getattr(self, f"description_{get_language()}")

    def image_tag(self):
        images = self.images.filter(is_main=True)
        if images.exists():
            image = images.first()
            return mark_safe('<img style="max-width:50px;max-height:75px;object-fit:contain" src="' +
                             "/media/"+str(image.thumbnail)+'" />')
        else:
            return "No image"

    def second_image(self):
        if self.images.all().count() > 1:
            return self.images.all()[1]
        elif self.images.all().count() == 1:
            return self.images.first()
        else:
            return "/static/images/logo.png"

    def main_image(self):
        return self.images.filter(is_main=True).first()

    @property
    def product_images(self):
        return self.images.all().order_by("-is_main")

    @property
    def sell_count(self):
        sum = self.transactions.aggregate(sum=Sum("count"))['sum']
        if sum:
            return sum
        else:
            return 0

    @property
    def sent_count(self):
        sum = self.transfers.aggregate(sum=Sum("count"))['sum']
        if sum:
            return sum
        else:
            return 0

    @property
    def sent_sell_count(self):
        sum = self.transactions.aggregate(sum=Sum("count", filter=Q(collaborator_id__gt=0)))['sum']
        if sum:
            return sum
        else:
            return 0

    @property
    def sent_not_sell_count(self):
        sum = self.transfers.aggregate(sum=Sum("count"))['sum']
        if sum:
            return sum - self.sent_sell_count
        else:
            return 0

    @property
    def sell_percent(self):
        if self.sell_count > 0:
            return float(self.sell_count)*100/self.total_count
        else:
            return 0

    @property
    def i_have(self):
        return self.total_count - self.sell_count - self.sent_not_sell_count


class ProductImage(models.Model):
    image = models.ImageField(upload_to="media/product", verbose_name=_("Image"))
    optimized = models.ImageField(upload_to="media/product/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to="media/product/middle_optimized",
                                         verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True, upload_to='media/product/thumb/', verbose_name=_("Thumbnail"))
    is_main = models.BooleanField(default=False, verbose_name=_("Is Main"))
    for_share = models.BooleanField(default=False, verbose_name=_("For Share"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False,
                                related_name="images", verbose_name=_("Product"))

    def resizeImg(self, img_size):
        img: IMG.Image = IMG.open(self.image)
        img.thumbnail(img_size, IMG.ANTIALIAS)
        outputIO = BytesIO()
        img.save(outputIO, format=img.format, quality=100)
        return outputIO, img

    def handleResize(self):
        imgSize = (100, 150)
        imgName = slugify(self.product.title_en) if self.product.title_en else slugify(self.product)
        outputIO, img = self.resizeImg(imgSize)
        return {
                'name': f'{imgName}.{img.format}',
                'content': ContentFile(outputIO.getvalue()),
                'save': False,
        }

    def handleOptimizedResize(self):
        imgSize = (500, 700)
        imgName = slugify(self.product.title_en) if self.product.title_en else slugify(self.product)
        outputIO, img = self.resizeImg(imgSize)
        return {
            'name': f'{imgName}.{img.format}',
            'content': ContentFile(outputIO.getvalue()),
            'save': False,
        }

    def handleMiddleOptimizedResize(self):
        imgSize = (250, 350)
        imgName = slugify(self.product.title_en) if self.product.title_en else slugify(self.product)
        outputIO, img = self.resizeImg(imgSize)
        return {
            'name': f'{imgName}.{img.format}',
            'content': ContentFile(outputIO.getvalue()),
            'save': False,
        }

    def save(self, *args, **kwargs):
        self.thumbnail.save(
            **self.handleResize()
        )
        self.optimized.save(
            **self.handleOptimizedResize()
        )
        self.middle_optimized.save(
            **self.handleMiddleOptimizedResize()
        )
        super().save(*args, **kwargs)

    def image_tag(self):
        if self.thumbnail:
            return mark_safe('<img style="max-width:50px;max-height:75px;object-fit:contain" src="' +
                             "/media/"+str(self.thumbnail)+'" />')
        else:
            return "No Image"


class Collaborator(models.Model):
    title_en = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Title English"))
    title_ru = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Title Russian"))
    title_hy = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Title Armenian"))
    description_en = models.TextField(verbose_name=_("Description English"))
    description_ru = models.TextField(verbose_name=_("Description Russian"))
    description_hy = models.TextField(verbose_name=_("Description Armenian"))
    address_en = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Address English"))
    address_ru = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Address Russian"))
    address_hy = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Address Armenian"))
    longitude = models.FloatField(null=True, blank=True, verbose_name=_("Longitude"))
    latitude = models.FloatField(null=True, blank=True, verbose_name=_("Latitude"))

    @property
    def title(self):
        return getattr(self, f"title_{get_language()}")

    @property
    def description(self):
        return getattr(self, f"description_{get_language()}")

    @property
    def address(self):
        return getattr(self, f"address_{get_language()}")

    def __str__(self):
        return self.title


class ProductTransaction(models.Model):
    count = models.PositiveIntegerField(null=False, blank=False, default=1, verbose_name=_("Count"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=False, blank=False,
                                related_name="transactions", verbose_name=_("Product"))
    amount = models.IntegerField(null=False, blank=False, verbose_name=_("Amount"))
    collaborator = models.ForeignKey(Collaborator, on_delete=models.PROTECT,
                                     null=True, blank=True, related_name="transactions", verbose_name=_("Collaborator"))
    type = models.CharField(choices=TRANSACTION_TYPES, blank=False, null=False, max_length=255, verbose_name=_("Type"))
    date = models.DateField(verbose_name=_("Date"), default=datetime.now())
    order = models.ForeignKey("core.Order", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Crated At"))

    @property
    def type_name(self):
        return [i for i in TRANSACTION_TYPES if i[0] == self.type][0][1]


class CostTransaction(models.Model):
    product_category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, null=True, blank=True,
                                         related_name="costs", verbose_name=_("Product Category"))
    amount = models.IntegerField(null=False, blank=False, verbose_name=_("Amount"))
    type = models.CharField(choices=COST_TYPES, blank=False, null=False, max_length=255, verbose_name=_("Type"))
    date = models.DateField(verbose_name=_("Date"), default=datetime.now())
    note = models.TextField(null=True, blank=True, verbose_name=_("Note"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    @property
    def cost_type_name(self):
        return [i for i in COST_TYPES if i[0] == self.type][0][1]


class Transfer(models.Model):
    count = models.PositiveIntegerField(null=False, blank=False, default=1, verbose_name=_("Count"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=False, blank=False,
                                related_name="transfers", verbose_name=_("Product"))
    amount = models.IntegerField(null=False, blank=False, verbose_name=_("Amount"))
    collaborator = models.ForeignKey(Collaborator, on_delete=models.PROTECT,
                                     related_name="transfers", verbose_name=_("Collaboratir"))
    date = models.DateField(verbose_name=_("Date"), default=datetime.now())
    note = models.TextField(null=True, blank=True, verbose_name=_("Note"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))


class ProductAuthor(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='authors')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_authors")


class ProductGame(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='games')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="games")


class SketchImage(models.Model):
    image = models.ImageField(upload_to="media/sketch", verbose_name=_("Image"))
    sketch = models.ImageField(verbose_name=_("Sketch Image"), blank=True, null=True,)
    thumbnail = models.ImageField(blank=True, null=True,
                                  upload_to='media/sketch/thumb/', verbose_name=_("Thumbnail"))

    def resizeImg(self, img_size):
        img: IMG.Image = IMG.open(self.image)
        img.thumbnail(img_size, IMG.ANTIALIAS)
        outputIO = BytesIO()
        img.save(outputIO, format=img.format, quality=100)
        return outputIO, img

    def handleResize(self):
        imgSize = (100, 150)
        imgName = str(time.time())
        outputIO, img = self.resizeImg(imgSize)
        return {
                'name': f'{imgName}.{img.format}',
                'content': ContentFile(outputIO.getvalue()),
                'save': False,
        }

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.thumbnail.save(
            **self.handleResize()
        )
        super().save(*args, **kwargs)

    def image_tag(self):
        if self.thumbnail:
            return mark_safe('<img style="max-width:50px;max-height:75px;object-fit:contain" src="' +
                             "/media/"+str(self.thumbnail)+'" />')
        else:
            return "No Image"
