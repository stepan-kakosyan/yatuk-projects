from django.contrib import admin
from django.urls import reverse_lazy

try:
    from tinymce.widgets import TinyMCE
    TINYMCE_AVAILABLE = True
except ImportError:
    TINYMCE_AVAILABLE = False

from .models import Category
from .models import Post
from .models import Tag

TINYMCE_CONFIG = {
    'theme': 'silver',
    'height': 400,
    'plugins': (
        'advlist autolink lists link image charmap print preview anchor '
        'searchreplace visualblocks code fullscreen insertdatetime media '
        'table paste code help wordcount'
    ),
    'toolbar': (
        'undo redo | formatselect | bold italic underline | '
        'alignleft aligncenter alignright alignjustify | '
        'bullist numlist outdent indent | link image media | '
        'removeformat code fullscreen'
    ),
    'images_upload_url': reverse_lazy('blog:upload-image'),
    'automatic_uploads': True,
    'image_caption': True,
    'file_picker_types': 'image',
    'content_css': '/static/blog/css/tinymce-content.css',
    'relative_urls': False,
    'remove_script_host': False,
}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title_hy', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('title_en',)}
    search_fields = ('title_hy', 'slug')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'title_hy', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('title_en',)}
    search_fields = ('title_hy', 'slug')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'view_count_total',
        'view_count_yatuk',
        'view_count_poem',
        'view_count_canvas',
        'status',
        'category',
        'published_at',
        'is_featured',
    )
    list_filter = ('status', 'is_featured', 'category', 'tags')
    search_fields = ('title', 'body', 'slug')
    autocomplete_fields = ('category', 'tags')
    fields = (
        'title',
        'slug',
        'excerpt',
        'body',
        'cover',
        'share_image',
        'status',
        'published_at',
        'is_featured',
        'category',
        'tags',
    )

    if TINYMCE_AVAILABLE:
        formfield_overrides = {
            __import__('django.db.models',
                       fromlist=['TextField']).TextField: {
                'widget': TinyMCE(
                    attrs={'cols': 80, 'rows': 30},
                    mce_attrs=TINYMCE_CONFIG
                )
            },
        }
