from django.db import models
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from users.models import User, State, Address

ORDER_STATUS = [
    ("not_paid", _("Not Paid")),
    ("accepted", _("Accepted")),
    ("in_process", _("In Process")),
    ("shipping", _("Shipping")),
    ("done", _("Done")),
    ("cancelled", _("Cancelled"))
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

    class Meta:
        db_table = 'product_productcategory'
        managed = False

    @property
    def title(self):
        return getattr(self, f"title_{get_language()}")

    @property
    def description(self):
        return getattr(self, f"description_{get_language()}")

    @property
    def category_products(self):
        return self.products.all()

    @property
    def icon_name(self):
        if self.title_en.lower() == "jigsaw puzzle":
            return "puzzle-piece"
        elif self.title_en.lower() == "bookmark":
            return "bookmark"
        elif self.title_en.lower() == "postcard":
            return "envelope"
        elif self.title_en.lower() == "game":
            return "gamepad"
        elif self.title_en.lower() == "magnet":
            return "magnet"
        elif self.title_en.lower() == "brooch":
            return "star"
        else:
            return "list"

class Product(models.Model):
    title_en = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title English"))
    title_ru = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Russian"))
    title_hy = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Armenian"))
    slug_en = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Slug English"))
    slug_ru = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Slug Russian"))
    slug_hy = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Slug Armenian"))
    description_en = models.TextField(verbose_name=_("Description English"))
    description_ru = models.TextField(verbose_name=_("Description Russian"))
    description_hy = models.TextField(verbose_name=_("Description Armenian"))
    price = models.IntegerField(null=False, blank=False, verbose_name=_("Price"))
    category = models.ForeignKey(ProductCategory, on_delete = models.PROTECT, null=False, 
                                 verbose_name=_("Category"), related_name="products")
    total_count = models.IntegerField(default=50, verbose_name=_("Total Count"))
    shop_url = models.CharField(null=True, blank=True, max_length=255)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True, verbose_name=_("Created At"))

    def __str__(self):
        return self.title

    @property
    def main_image(self):
        return self.images.filter(is_main=True).first()

    def for_share_image(self):
        return self.images.filter(for_share = True).first()

    @property
    def title(self):
        return getattr(self, f"title_{get_language()}")

    @property
    def description(self):
        return getattr(self, f"description_{get_language()}")

    @property
    def product_images(self):
        return self.images.filter(is_main=False)

    @property
    def author(self):
        return self.product_authors.all().first().author.name_hy
        
    class Meta:
        db_table = 'product_product'
        managed = False

class ProductImage(models.Model):
    image = models.ImageField(upload_to = "media/product", verbose_name=_("Image"))
    optimized = models.ImageField(upload_to = "media/product/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to = "media/product/middle_optimized", verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,upload_to ='media/product/thumb/', verbose_name=_("Thumbnail"))
    is_main = models.BooleanField(default=True, verbose_name=_("Is Main"))
    for_share = models.BooleanField(default=False, verbose_name=_("For Share"))
    product = models.ForeignKey(Product, on_delete = models.CASCADE, null=False, blank=False,
                                related_name="images", verbose_name=_("Product"))

    class Meta:
        db_table = 'product_productimage'
        managed = False

class ContactUs(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Name"))
    email_or_phone = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Email or Phone Number"))
    text = models.TextField(max_length=2000, null=False, blank=False, verbose_name=_("Text"))
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
    main_image = models.ImageField(upload_to = "media/slider", verbose_name=_("Main Image"))
    blur_image = models.ImageField(upload_to = "media/slider", verbose_name=_("Blur Image"))
    link = models.CharField(max_length=255, null=True, blank=True)
    
    @property
    def title(self):
        return getattr(self, f"title_{get_language()}")

    @property
    def description(self):
        return getattr(self, f"description_{get_language()}")

    class Meta:
        db_table = 'core_slider'
        managed = False

class ShoppingCart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="products", null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_products", null=False, blank=False)
    count = models.PositiveIntegerField(null=False, blank=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_shoppingcart'
        managed = False

class ShippingMethod(models.Model):
    title_en = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title English"))
    title_ru = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Russian"))
    title_hy = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Armenian"))
    description_en = models.TextField(verbose_name=_("Description English"))
    description_ru = models.TextField(verbose_name=_("Description Russian"))
    description_hy = models.TextField(verbose_name=_("Description Armenian"))
    image = models.ImageField(upload_to = "media/slider", verbose_name=_("Main Image"))
    price = models.IntegerField(null=False, blank=False, verbose_name=_("Price"))
    states_available = models.ManyToManyField(State, related_name="states")

    def __str__(self):
        return f'{self.title_en}'

    class Meta:
        db_table = 'core_shippingmethod'
        managed = False

    @property
    def description(self):
        return getattr(self, f"description_{get_language()}")

    @property
    def title(self):
        return getattr(self, f"title_{get_language()}")

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.PROTECT, related_name='orders',
                                        null=False, blank=False, verbose_name=_("Shipping Method"))
    shipping_price = models.IntegerField(null=False, blank=False, verbose_name=_("Shipping Price"))
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='orders',
                                        null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_id = models.CharField(max_length=100, blank=True)
    shipping_number = models.CharField(max_length=100, blank=True, null=True)
    amount = models.PositiveIntegerField(null=False, blank=False, verbose_name=_("Amount"))
    status = models.CharField(choices=ORDER_STATUS, blank=False, null=False, max_length=255,
                              verbose_name=_("Status"))
    comment = models.TextField(null=True, blank=True, verbose_name=_("Comment"))
    phone_number = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Phone number"))

    def __str__(self):
        return f'Order #{self.id}'

    @property
    def status_display(self):
        return list(filter(lambda x: x[0] == self.status, ORDER_STATUS))[0][1]

    class Meta:
        db_table = 'core_order'
        managed = False

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(null=False, blank=False, verbose_name=_("Price"))
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product}'

    class Meta:
        db_table = 'core_orderitem'
        managed = False

class ProductTransaction(models.Model):
    count = models.PositiveIntegerField(null=False, blank=False, default=1, verbose_name=_("Count"))
    product = models.ForeignKey(Product, on_delete = models.PROTECT, null=False, blank=False, 
                                related_name = "transactions", verbose_name=_("Product"))
    amount = models.IntegerField(null=False, blank=False, verbose_name=_("Amount"))
    type = models.CharField(blank=False, null=False, max_length=255, verbose_name=_("Type"))
    date = models.DateField(verbose_name=_("Date"))
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True, verbose_name=_("Crated At"))

    class Meta:
        db_table = 'product_producttransaction'
        managed = False

class Author(models.Model):
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)    
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    bio_hy = models.TextField(null=True, blank=True)
    bio_en = models.TextField(null=True, blank=True)    
    bio_ru = models.TextField(null=True, blank=True)
    dates = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='authors/')
    main_image = models.ImageField(upload_to='authors/')
    slug = models.SlugField(unique=True, null=True, blank=True)
    optimized = models.ImageField(upload_to = "media/product/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to = "media/product/middle_optimized", verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,upload_to ='media/product/thumb/', verbose_name=_("Thumbnail"))

    class Meta:
        db_table = 'core_game_author'
        managed = False

    @property
    def name(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def bio(self):
        return getattr(self, f"bio_{get_language()}") if getattr(self, f"bio_{get_language()}") else ""


class Game(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=False, blank=False, related_name="games")
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)    
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to='game/')
    main_color = models.CharField(max_length=255, null=True, blank=True)
    pid = models.CharField(max_length=255, null=False, blank=False)
    played_count = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(unique=True, null=False, blank=True)
    background_position = models.CharField( max_length=255, default="center", blank=False)
    optimized = models.ImageField(upload_to = "media/product/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to = "media/product/middle_optimized", verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,upload_to ='media/product/thumb/', verbose_name=_("Thumbnail"))

    class Meta:
        db_table = 'core_game_game'
        managed = False

    @property
    def name(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def author_name(self):
        return getattr(self.author, f"name_{get_language()}")


class ProductAuthor(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='authors')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_authors")

    class Meta:
        db_table = 'product_productauthor'
        managed = False


class ProductGame(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='games')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="games")

    class Meta:
        db_table = 'product_productgame'
        managed = False


class Review(models.Model):
    image = models.ImageField(upload_to='review/')
    name = models.CharField(max_length=255, null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    star = models.PositiveSmallIntegerField(default=5)
    date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    facebook_link = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'core_review'
        managed = False
