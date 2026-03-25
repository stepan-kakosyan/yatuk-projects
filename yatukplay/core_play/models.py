from django.db import models
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from utils.slugs import unique_slug_generator


class Author(models.Model):
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    quote_hy = models.CharField(max_length=500, null=True, blank=True)
    quote_en = models.CharField(max_length=500, null=True, blank=True)
    quote_ru = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='authors/')
    optimized = models.ImageField(upload_to="media/authors/optimized",
                                  verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to="media/authors/middle_optimized",
                                         verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,
                                  upload_to='media/authors/thumb/', verbose_name=_("Thumbnail"))
    slug = models.SlugField(unique=True, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_hy

    class Meta:
        db_table = 'core_play_author'
        managed = False

    @property
    def name(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def quote(self):
        return getattr(self, f"quote_{get_language()}") if getattr(self, f"quote_{get_language()}") else ""


class Audio(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=False, blank=False, related_name="musics")
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to='authors/')
    optimized = models.ImageField(upload_to="media/authors/optimized",
                                  verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to="media/authors/middle_optimized",
                                         verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True, upload_to='media/authors/thumb/',
                                  verbose_name=_("Thumbnail"))
    audio = models.FileField(upload_to='audios/')
    played_count = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(unique=True, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_play_audio'
        managed = False

    def save(self):
        if not self.pk:
            self.slug = unique_slug_generator(self)
        return super().save()

    @property
    def title(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def author_name(self):
        return getattr(self.author, f"name_{get_language()}")

    def __str__(self):
        return self.title


class ProductCategory(models.Model):
    title_en = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Title English"))
    title_ru = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Title Russian"))
    title_hy = models.CharField(max_length=255, null=False, blank=False, verbose_name=_("Title Armenian"))
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
    def icon_display(self):
        if self.title_en == "Bookmark":
            return "bookmark"
        elif self.title_en == "Postcard":
            return "envelope"
        else:
            return "puzzle-piece"

    @property
    def title(self):
        return getattr(self, f"title_{get_language()}")

    @property
    def description(self):
        return getattr(self, f"description_{get_language()}")


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
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, null=False,
                                 verbose_name=_("Category"), related_name="products")
    total_count = models.IntegerField(default=50, verbose_name=_("Total Count"))
    shop_url = models.CharField(null=True, blank=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return self.title

    def main_image(self):
        return self.images.filter(for_share=True).first()

    @property
    def title(self):
        return getattr(self, f"title_{get_language()}")

    @property
    def description(self):
        return getattr(self, f"description_{get_language()}")

    class Meta:
        db_table = 'product_product'
        managed = False


class ProductImage(models.Model):
    image = models.ImageField(upload_to="media/product", verbose_name=_("Image"))
    optimized = models.ImageField(upload_to="media/product/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to="media/product/middle_optimized",
                                         verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,
                                  upload_to='media/product/thumb/', verbose_name=_("Thumbnail"))
    is_main = models.BooleanField(default=True, verbose_name=_("Is Main"))
    for_share = models.BooleanField(default=False, verbose_name=_("For Share"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False,
                                related_name="images", verbose_name=_("Product"))

    class Meta:
        db_table = 'product_productimage'
        managed = False
