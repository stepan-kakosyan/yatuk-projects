import os

from django.apps import apps
from django.conf import settings
from django.db import IntegrityError
from django.db.models import F
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView
from django.views.generic import ListView

from .models import Category
from .models import Post
from .models import PostView
from .models import Tag


BLOG_MEDIA_HOST = getattr(settings, 'BLOG_MEDIA_HOST', '')


def get_view_domain(request):
    host = request.get_host().split(':')[0].lower()
    if host == 'yatuk.am':
        return PostView.Domain.YATUK
    if host == 'poem.yatuk.am':
        return PostView.Domain.POEM
    if host == 'canvas.yatuk.am':
        return PostView.Domain.CANVAS
    return None


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '').strip()


def get_random_products(limit=8):
    """Return random products from whichever app provides Product model."""
    model_candidates = [
        ('core', 'Product'),
        ('core_game', 'Product'),
        ('core_play', 'Product'),
        ('product', 'Product'),
    ]

    for app_label, model_name in model_candidates:
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            continue

        if model is None:
            continue

        queryset = model.objects.all()
        if hasattr(model, 'is_finished'):
            queryset = queryset.filter(is_finished=False)

        return queryset.order_by('?')[:limit]

    return []


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 12

    def get_queryset(self):
        queryset = Post.objects.published().select_related(
            'category'
        ).prefetch_related('tags')

        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title_hy__icontains=search_query)
                | Q(excerpt_hy__icontains=search_query)
                | Q(body_hy__icontains=search_query)
            )

        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        tag_slugs = self.request.GET.getlist('tags')
        if tag_slugs:
            tag_query = Q()
            for tag_slug in tag_slugs:
                tag_query |= Q(tags__slug=tag_slug)
            queryset = queryset.filter(tag_query)

        return queryset.distinct()

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['blog/post_list_partial.html']
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('title_hy')
        context['tags'] = Tag.objects.all().order_by('title_hy')
        context['current_search'] = self.request.GET.get('q', '').strip()
        context['current_category'] = self.request.GET.get('category', '')
        context['current_tags'] = self.request.GET.getlist('tags', [])
        context['blog_media_host'] = BLOG_MEDIA_HOST
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def _record_view(self, post):
        domain = get_view_domain(self.request)
        if not domain:
            return

        device_id = get_client_ip(self.request)
        if not device_id:
            return

        viewed_date = timezone.localdate()

        try:
            _, created = PostView.objects.get_or_create(
                post=post,
                device_id=device_id,
                viewed_date=viewed_date,
                domain=domain,
            )
        except IntegrityError:
            created = False

        if not created:
            return

        updates = {'view_count_total': F('view_count_total') + 1}
        if domain == PostView.Domain.YATUK:
            updates['view_count_yatuk'] = F('view_count_yatuk') + 1
        elif domain == PostView.Domain.POEM:
            updates['view_count_poem'] = F('view_count_poem') + 1
        elif domain == PostView.Domain.CANVAS:
            updates['view_count_canvas'] = F('view_count_canvas') + 1

        Post.objects.filter(pk=post.pk).update(**updates)
        post.refresh_from_db(
            fields=[
                'view_count_total',
                'view_count_yatuk',
                'view_count_poem',
                'view_count_canvas',
            ]
        )

    def get_object(self, queryset=None):
        queryset = Post.objects.published().select_related(
            'category'
        ).prefetch_related('tags')
        post = get_object_or_404(queryset, slug=self.kwargs['slug'])
        self._record_view(post)
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog_media_host'] = BLOG_MEDIA_HOST
        context['products'] = get_random_products(limit=8)
        context['featured_posts'] = Post.objects.filter(
            Q(category=self.object.category) |
            Q(tags__in=self.object.tags.all()) |
            Q(is_featured=True)
        ).exclude(id=self.object.id).distinct().order_by(
            'is_featured',
            '-created_at',
        )[:4]
        return context


@csrf_exempt
@require_http_methods(["GET", "POST"])
def upload_image(request):
    """
    Handle TinyMCE image uploads.
    Saves uploaded image to blog/media/covers/ and returns JSON response.
    """
    if request.method == 'GET':
        return JsonResponse(
            {
                'detail': (
                    'Use POST with multipart/form-data '
                    'to upload an image.'
                ),
                'field': 'file',
                'upload_url': reverse('blog:upload-image'),
            },
            status=200,
        )

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    uploaded_file = request.FILES['file']

    # Validate file is an image
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in allowed_extensions:
        return JsonResponse({'error': 'Invalid file type'}, status=400)

    # Create media directory if it doesn't exist
    media_root = settings.MEDIA_ROOT
    blog_covers_dir = os.path.join(media_root, 'blog', 'covers')
    os.makedirs(blog_covers_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(blog_covers_dir, uploaded_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    # Return the URL to the uploaded file
    file_url = f"{settings.MEDIA_URL}blog/covers/{uploaded_file.name}"

    return JsonResponse({'location': file_url})
