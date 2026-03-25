from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

try:
    from tinymce.models import HTMLField
except ImportError:
    HTMLField = models.TextField


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    title_en = models.CharField(max_length=255, verbose_name=_('Title English'))
    title_ru = models.CharField(max_length=255, verbose_name=_('Title Russian'))
    title_hy = models.CharField(max_length=255, verbose_name=_('Title Armenian'))
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = 'blog_category'
        ordering = ['title_hy']

    def __str__(self):
        return self.title

    @property
    def title(self):
        return self.title_hy


class Tag(TimeStampedModel):
    title_en = models.CharField(max_length=255, verbose_name=_('Title English'))
    title_ru = models.CharField(max_length=255, verbose_name=_('Title Russian'))
    title_hy = models.CharField(max_length=255, verbose_name=_('Title Armenian'))
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = 'blog_tag'
        ordering = ['title_hy']

    def __str__(self):
        return self.title

    @property
    def title(self):
        return self.title_hy


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Post.Status.PUBLISHED)


class Post(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='posts',
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    title = models.CharField(max_length=255, verbose_name=_('Title Armenian'))
    slug = models.SlugField(unique=True)
    excerpt = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_('Excerpt Armenian'),
    )
    body = HTMLField(verbose_name=_('Body'))
    cover = models.ImageField(upload_to='blog/covers/', null=True, blank=True)
    share_image = models.ImageField(
        upload_to='blog/share/',
        null=True,
        blank=True,
        verbose_name=_('Share Image'),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    published_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    view_count_total = models.PositiveIntegerField(default=0)
    view_count_yatuk = models.PositiveIntegerField(default=0)
    view_count_poem = models.PositiveIntegerField(default=0)
    view_count_canvas = models.PositiveIntegerField(default=0)

    objects = PostQuerySet.as_manager()

    class Meta:
        db_table = 'blog_post'
        ordering = ['-published_at', '-id']
        indexes = [
            models.Index(fields=['status', 'published_at']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})


class PostView(TimeStampedModel):
    class Domain(models.TextChoices):
        YATUK = 'yatuk', 'yatuk.am'
        POEM = 'yatukpoem', 'poem.yatuk.am'
        CANVAS = 'yatukcanvas', 'canvas.yatuk.am'

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='views',
    )
    device_id = models.CharField(max_length=64)
    viewed_date = models.DateField()
    domain = models.CharField(max_length=20, choices=Domain.choices)

    class Meta:
        db_table = 'blog_post_view'
        ordering = ['-created_at', '-id']
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'device_id', 'viewed_date', 'domain'],
                name='uniq_blog_view_post_device_day_domain',
            )
        ]
        indexes = [
            models.Index(fields=['post', 'domain']),
            models.Index(fields=['viewed_date']),
        ]

    def __str__(self):
        return f'{self.post_id}:{self.domain}:{self.viewed_date}'
