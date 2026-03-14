from django.db import models
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from users.models import User
from django.urls import reverse_lazy
from utils.functions import no_tag


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


class ProductTransaction(models.Model):
    count = models.PositiveIntegerField(null=False, blank=False, default=1, verbose_name=_("Count"))
    product = models.ForeignKey(Product, on_delete = models.PROTECT, null=False, blank=False, 
                                related_name = "transactions", verbose_name=_("Product"))
    amount = models.IntegerField(null=False, blank=False, verbose_name=_("Amount"))
    type = models.CharField(blank=False, null=False, max_length=255, verbose_name=_("Type"))
    date = models.DateField(verbose_name=_("Date"))

    class Meta:
        db_table = 'product_producttransaction'
        managed = False


class GameAuthor(models.Model):
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
    signature = models.ImageField(upload_to='authors/', null=True, blank=True)

    class Meta:
        db_table = 'core_game_author'
        managed = False

    @property
    def image_(self):
        return self.main_image if self.main_image else self.image

    @property
    def has_photo(self):
        return self.photos.count() > 0

    @property
    def name(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def bio(self):
        return getattr(self, f"bio_{get_language()}") if getattr(self, f"bio_{get_language()}") else ""

    @property
    def url(self):
        game = Game.objects.filter(author=self).order_by("?").first()
        return f"https://canvas.yatuk.am/hy/{self.slug}/{game.slug}"

    def __str__(self):
        return getattr(self, f"name_{get_language()}")


class Game(models.Model):
    author = models.ForeignKey(GameAuthor, on_delete=models.CASCADE, null=False, blank=False, related_name="games")
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

    @property
    def main_url(self):
        return reverse_lazy('game', args=[self.author.slug, self.slug, self.id])


class ProductGame(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='games')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="games")

    class Meta:
        db_table = 'product_productgame'
        managed = False


class Genre(models.Model):
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)    
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name_hy

    class Meta:
        db_table = 'poem_genre'
        managed = False

    @property
    def name(self):
        return getattr(self, f"name_{get_language()}")


class PoemAuthor(models.Model):
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)    
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    dates = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='authors/')
    signature = models.ImageField(upload_to='authors/', null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    optimized = models.ImageField(upload_to = "media/product/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to = "media/product/middle_optimized", verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,upload_to ='media/product/thumb/', verbose_name=_("Thumbnail"))

    class Meta:
        db_table = 'poem_author'
        managed = False

    def __str__(self):
        return self.name_hy

    @property
    def name(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def poem_count(self):
        return self.poems.count()


    @property
    def url(self):
        return f"https://poem.yatuk.am/hy/author/{self.slug}/all/"


class Poem(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=False, blank=False, related_name="poems")
    author = models.ForeignKey(PoemAuthor, on_delete=models.CASCADE, null=False, blank=False, related_name="poems")
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True, related_name="poems")
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=True, blank=True)    
    name_ru = models.CharField(max_length=255, null=True, blank=True)
    content_hy = models.TextField( null=False, blank=False)
    content_en = models.TextField( null=True, blank=True) 
    content_ru = models.TextField( null=True, blank=True)
    view_count = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(unique=True, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'poem_poem'
        managed = False


    @property
    def name(self):
        return self.name_hy

    @property
    def content(self):
        return no_tag(self.content_hy)

    @property
    def author_name(self):
        return getattr(self.author, f"name_{get_language()}")

    @property
    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return self.author.name_hy +" - " + self.name_hy


class Label(models.Model):
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)    
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(unique=True, null=True, blank=True)
 
    class Meta:
        db_table = 'poem_label'
        managed = False

    def __str__(self):
        return self.name_hy


class PoemLabel(models.Model):
    label = models.ForeignKey(Label, on_delete=models.CASCADE, null=False, blank=False, related_name="poems")
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, null=False, blank=False, related_name="labels")

    class Meta:
        db_table = 'poem_poemlabel'
        managed = False


class PoemSection(models.Model):
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, null=False, blank=False, related_name="sections")
    order = models.IntegerField(default=2, null=False, blank=False)
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=True, blank=True)    
    name_ru = models.CharField(max_length=255, null=True, blank=True)
    content_hy = models.TextField(null=True, blank=True)
    content_en = models.TextField(null=True, blank=True)
    content_ru = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name_hy

    class Meta:
        db_table = 'poem_poemsection'
        managed = False

    @property
    def name(self):
        return self.name_hy

    @property
    def content(self):
        return no_tag(self.content_hy)


class AudioAuthor(models.Model):
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)    
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    quote_hy = models.CharField(max_length=500, null=True, blank=True)
    quote_en = models.CharField(max_length=500, null=True, blank=True)    
    quote_ru = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='authors/')
    optimized = models.ImageField(upload_to = "media/authors/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to = "media/authors/middle_optimized", verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,upload_to ='media/authors/thumb/', verbose_name=_("Thumbnail"))
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

    @property
    def url(self):
        audio = Audio.objects.filter(author=self).order_by("?").first()
        return f"https://play.yatuk.am/hy/music/{self.slug}/{audio.slug}"


class Audio(models.Model):
    author = models.ForeignKey(AudioAuthor, on_delete=models.CASCADE, null=False, blank=False, related_name="musics")
    name_hy = models.CharField(max_length=255, null=False, blank=False)
    name_en = models.CharField(max_length=255, null=False, blank=False)    
    name_ru = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to='authors/')
    optimized = models.ImageField(upload_to = "media/authors/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to = "media/authors/middle_optimized", verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,upload_to ='media/authors/thumb/', verbose_name=_("Thumbnail"))
    audio = models.FileField(upload_to='audios/')
    played_count = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(unique=True, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_play_audio'
        managed = False

    @property
    def next_id(self):
        try:
            return Audio.objects.filter(id__gt=self.id).exclude(author=self.author).order_by('id').first().id
        except:
            return Audio.objects.exclude(id=self.id).first().id

    @property
    def prev_id(self):
        try:
            return Audio.objects.filter(id__lt=self.id).exclude(author=self.author).order_by('-id').first().id
        except:
            return Audio.objects.exclude(id=self.id).first().id
    @property
    def title(self):
        return getattr(self, f"name_{get_language()}")

    @property
    def author_name(self):
        return getattr(self.author, f"name_{get_language()}")

    def __str__(self):
        return self.title


class Like(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False, blank=False, related_name="likes")
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE, null=False, blank=False, related_name="likes")
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, null=False, blank=False, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'poem_like'
        managed = False


class Favorite(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False, blank=False, related_name="favorites")
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE, null=False, blank=False, related_name="favorites")
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, null=False, blank=False, related_name="favorites")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="favorites")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'poem_favorite'
        managed = False


class WantToRead(models.Model):
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, null=False, blank=False, related_name="want_to_reads")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="want_to_reads")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'poem_wanttoread'
        managed = False


class PoemComment(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False, blank=False, related_name="comments")
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE, null=False, blank=False, related_name="comments")
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, null=False, blank=False, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="comments")
    text = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'poem_poemcomment'
        managed = False


class Photo(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(unique=False, null=False, blank=True)
    image = models.ImageField(upload_to='photo/')
    created_at = models.DateTimeField(auto_now_add=True)
    optimized = models.ImageField(upload_to = "media/photo/optimized", verbose_name=_("Image"), null=True, blank=True)
    middle_optimized = models.ImageField(upload_to = "media/photo/middle_optimized", verbose_name=_("Image"), null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True,upload_to ='media/photo/thumb/', verbose_name=_("Thumbnail"))
    background_position = models.CharField( max_length=255, default="center", blank=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'poem_photo'
        managed = False


class PhotoPerson(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=False, blank=False, related_name="photos")
    writer = models.ForeignKey(PoemAuthor, on_delete=models.CASCADE, null=True, blank=True, related_name="photos")
    composer = models.ForeignKey(AudioAuthor, on_delete=models.CASCADE, null=True, blank=True, related_name="photos")
    painter = models.ForeignKey(GameAuthor, on_delete=models.CASCADE, null=True, blank=True, related_name="photos")
    text = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'poem_photoperson'
        managed = False
