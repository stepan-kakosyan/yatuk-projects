from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.translation import check_for_language
from django.http import HttpResponseRedirect
from core.models import (Genre, PoemAuthor, Poem, PoemSection, Audio, Like,
                         Favorite, WantToRead, AuthorBio,
                         AuthorQuote, PoemComment, Photo,
                         GameAuthor, AudioAuthor, Game, Product)
from .forms import ContactUsForm, PoemCommentForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from utils.functions import send_yatuk_email
from django.utils.translation import activate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils.functions import check_user_login, no_tag
from django.db.models import Exists, OuterRef, Q
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO, StringIO


def set_language(request):
    lang_code = request.GET.get('language', settings.LANGUAGE_CODE)
    next_url = "/"+lang_code+"/"
    nurl = request.GET.get('next_url', None)
    if nurl:
        nurl = nurl[4:]
        next_url += nurl
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
        "form": ContactUsForm(),
        'most_populars': Poem.objects.all().order_by('-view_count')[:15],
        "authors": PoemAuthor.objects.filter(
            poems__isnull=False).order_by("?").distinct()[:10],
        "carousel_items": Poem.objects.all().order_by('?')[:15]
    }
    return render(request, 'core/index.html', context=ctx)


def authors(request):
    ctx = {
        "active": "authors",
        "authors": PoemAuthor.objects.filter(
            poems__isnull=False).order_by("name_hy").distinct()
    }
    return render(request, 'core/authors.html', context=ctx)


def contact_us(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            form.save()
            html_content = render_to_string(
                'emails/contact-us.html', {'contact_details': cd})
            send_yatuk_email(subject=f"Կապ մեզ հետ՝ {cd['name']}",
                             message=f"Կապ մեզ հետ՝ {cd['name']}",
                             to_=["contact@yatuk.am",
                                  "stepankakosyan22@gmail.com"],
                             from_="info@yatuk.am",
                             html=html_content)
            messages.success(request, _('Your message was successfully sent.'))
            return render(request, 'core/partials/contact-form.html',
                          {"form": ContactUsForm})
    else:
        form = ContactUsForm()
    ctx = {
        "active": "contact_us",
        'form': form
    }
    if request.htmx:
        return render(request, 'core/partials/contact-form.html', ctx)
    return render(request, 'core/contact-us.html', ctx)


def author(request, slug, genre=None):
    genre = genre if genre else "all"
    author = PoemAuthor.objects.get(slug=slug)
    if request.user.is_authenticated:
        qs = Poem.objects.select_related("author").filter(
            author=author).annotate(
                favorite=Exists(
                    Favorite.objects.filter(user=request.user,
                                            poem_id=OuterRef("pk"))
                ), want_to_read=Exists(
                    WantToRead.objects.filter(
                        user=request.user, poem_id=OuterRef("pk"))
                    ))
        if genre != "all":
            qs = qs.filter(genre__slug=genre)
        qs = qs.order_by('-want_to_read', '-favorite', 'name_hy')
    else:
        qs = Poem.objects.select_related("author").filter(author=author)
        if genre != "all":
            qs = qs.filter(genre__slug=genre)
        qs = qs.order_by('name_hy')
    paginator = Paginator(qs, per_page=12)
    page = request.GET.get('page', 1)
    try:
        poems = paginator.page(page)
    except PageNotAnInteger:
        poems = paginator.page(1)
    except EmptyPage:
        poems = paginator.page(paginator.num_pages)
    genres = Genre.objects.filter(poems__author=author).distinct()
    hide_filters = genres.count() == 1

    ctx = {
        "author": author,
        "poems": poems,
        "selected_genre": genre,
        "genres": genres,
        'hide_filters': hide_filters,
        'active': 'poems'
    }
    if request.htmx:
        return render(request, 'core/partials/poem-list.html', context=ctx)
    return render(request, 'core/author.html', context=ctx)


def author_bio(request, slug):
    author = PoemAuthor.objects.get(slug=slug)
    bio = AuthorBio.objects.get(author__slug=slug)
    ctx = {
        "author": author,
        'bio': bio,
        'active': 'biography'
    }
    return render(request, 'core/author-bio.html', context=ctx)


def author_quotes(request, slug):
    author = PoemAuthor.objects.get(slug=slug)
    quotes = AuthorQuote.objects.get(author__slug=slug)
    ctx = {
        "author": author,
        'quotes': quotes,
        'active': 'quotes'
    }
    return render(request, 'core/author-quotes.html', context=ctx)


def author_photoarchive(request, slug):
    author = PoemAuthor.objects.get(slug=slug)
    photos = Photo.objects.filter(photos__writer_id=author.id).distinct()
    ctx = {
        "author": author,
        'photos': photos,
        'active': 'photoarchive'
    }
    if request.htmx:
        return render(request, 'core/partials/photoarchive.html', context=ctx)
    return render(request, 'core/author-photoarchive.html', context=ctx)


def poem(request, author, slug, id):
    _section = request.GET.get('section', None)
    poem = Poem.objects.select_related("author").get(id=id)
    if poem.author.slug != author or poem.slug != slug:
        return redirect(poem.main_url, permanent=True)
    if _section:
        active_section = PoemSection.objects.get(poem=poem, order=_section)
    else:
        active_section = None
    if request.user.is_authenticated:
        poem.liked = poem.likes.filter(user=request.user).exists()
        poem.favorite = poem.favorites.filter(user=request.user).exists()
        poem.want_to_read = poem.want_to_reads.filter(
            user=request.user).exists()
    song = Audio.objects.order_by("?").first()
    products = Product.objects.filter(is_finished=False).order_by('?')[:8]
    poem.view_count = 1 if not poem.view_count else poem.view_count + 1
    poem.save()
    ctx = {
        "author": author,
        "poem": poem,
        'song': song,
        "products": products,
        'form': PoemCommentForm(),
        'active_section': active_section,
        'sections': PoemSection.objects.filter(poem=poem),
        'comments': PoemComment.objects.filter(poem=poem).order_by('-id')
    }
    return render(request, 'core/poem.html', context=ctx)


def reading_poem(request, id):
    _section = request.GET.get('section', None)
    poem = Poem.objects.get(id=id)
    if _section:
        active_section = PoemSection.objects.get(poem=poem, order=_section)
    else:
        active_section = None
    ctx = {
        "author": author,
        "poem": poem,
        'active_section': active_section,
    }
    return render(request, 'core/reading-poem.html', context=ctx)


def music(request):
    id = request.GET.get("id")
    song = Audio.objects.get(id=id)
    return render(request, 'core/partials/music-card.html',
                  context={'song': song})


def set_theme(request):
    theme = request.GET.get('theme', "light")
    if hasattr(request, 'session'):
        request.session['theme'] = theme
    request.session.set_expiry(75686400)
    if request.user.is_authenticated:
        request.user.background = theme
        request.user.save()
    return HttpResponse("")


def privacy_policy(request):
    return render(request, 'core/privacy-policy.html')


def terms_and_conditions(request):
    return render(request, 'core/terms-and-conditions.html')


def like(request, id):
    poem = Poem.objects.get(id=id)
    check_user = check_user_login(request=request, next=poem.main_url)
    if not check_user:
        return check_user
    like = Like.objects.filter(user=request.user, poem_id=id)
    if like:
        like.delete()
        poem.liked = False
    else:
        like = Like(user=request.user, poem_id=id)
        like.save()
        poem.liked = True
    poem.favorite = poem.favorites.filter(user=request.user).exists()
    poem.want_to_read = poem.want_to_reads.filter(user=request.user).exists()
    return render(request, 'core/partials/like.html', context={'poem': poem})


def favorite(request, id):
    poem = Poem.objects.get(id=id)
    check_user = check_user_login(request=request, next=poem.main_url)
    if not check_user:
        return check_user
    favorite = Favorite.objects.filter(user=request.user, poem_id=id)
    if favorite:
        favorite.delete()
        poem.favorite = False
    else:
        favorite = Favorite(user=request.user, poem_id=id)
        favorite.save()
        poem.favorite = True
    poem.liked = poem.likes.filter(user=request.user).exists()
    poem.want_to_read = poem.want_to_reads.filter(user=request.user).exists()
    return render(request, 'core/partials/like.html', context={'poem': poem})


def want_to_read(request, id):
    poem = Poem.objects.get(id=id)
    check_user = check_user_login(request=request, next=poem.main_url)
    if not check_user:
        return check_user
    want_to_read = WantToRead.objects.filter(user=request.user, poem_id=id)
    if want_to_read:
        want_to_read.delete()
        poem.want_to_read = False
    else:
        want_to_read = WantToRead(user=request.user, poem_id=id)
        want_to_read.save()
        poem.want_to_read = True
    poem.liked = poem.likes.filter(user=request.user).exists()
    poem.favorite = poem.favorites.filter(user=request.user).exists()
    return render(request, 'core/partials/like.html', context={'poem': poem})


@login_required
def saved(request):
    qs = Poem.objects.filter(favorites__user=request.user)
    qs = qs.order_by('name_hy')
    paginator = Paginator(qs, per_page=12)
    page = request.GET.get('page', 1)
    try:
        poems = paginator.page(page)
    except PageNotAnInteger:
        poems = paginator.page(1)
    except EmptyPage:
        poems = paginator.page(paginator.num_pages)
    ctx = {
        "poems": poems,
    }
    if request.htmx:
        return render(request, 'core/partials/saved-poem-list.html',
                      context=ctx)
    return render(request, 'core/saved.html', context=ctx)


@login_required
def want_read(request):
    qs = Poem.objects.filter(want_to_reads__user=request.user)
    qs = qs.order_by('name_hy')
    paginator = Paginator(qs, per_page=12)
    page = request.GET.get('page', 1)
    try:
        poems = paginator.page(page)
    except PageNotAnInteger:
        poems = paginator.page(1)
    except EmptyPage:
        poems = paginator.page(paginator.num_pages)
    ctx = {
        "poems": poems,
    }
    if request.htmx:
        return render(request, 'core/partials/want-read-poem-list.html',
                      context=ctx)
    return render(request, 'core/want-read.html', context=ctx)


def html2pdf(request, id):
    poem = Poem.objects.get(id=id)
    section = request.GET.get('section', None)
    if section:
        poem_section = PoemSection.objects.get(id=section)
    else:
        poem_section = None
    template = get_template("core/pdf.html")
    html = template.render(context={'poem': poem, 'section': poem_section})
    result = BytesIO()
    pdf = pisa.CreatePDF(StringIO(html), result, encoding='utf-8')
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    f_name = f'attachment; filename="{poem.author.slug}-{poem.slug}.pdf'
    response['Content-Disposition'] = f_name
    if not pdf.err:
        if request.GET.get('for_print', None):
            return HttpResponse(result.getvalue(),
                                content_type='application/pdf')
        else:
            return response
    return None


def comment(request, id):
    if request.method == 'POST':
        poem = Poem.objects.get(id=id)
        check_user = check_user_login(request=request, next=poem.main_url)
        if not check_user:
            return check_user
        form = PoemCommentForm(request.POST)

        if form.is_valid():
            comment = PoemComment(text=form.cleaned_data['text'],
                                  user=request.user,
                                  poem=poem)
            comment.save()
            ctx = {
                'form': PoemCommentForm(),
                'poem': poem,
                'comments': PoemComment.objects.filter(
                    poem=poem).order_by('-id')
            }
            return render(request, 'core/partials/comment-form.html', ctx)
        ctx = {
            'form': PoemCommentForm(request.POST),
            'poem': poem,
            'comments': PoemComment.objects.filter(poem=poem).order_by('-id')
        }
        return render(request, 'core/partials/comment-form.html', ctx)


def search(request):
    genre = request.GET.get('genre', "all")
    author = request.GET.get('author', "all")
    search = request.GET.get('search', "")
    if request.user.is_authenticated:
        qs = Poem.objects.annotate(
            favorite=Exists(
                Favorite.objects.filter(
                    user=request.user, poem_id=OuterRef("pk"))
                ), want_to_read=Exists(
                    WantToRead.objects.filter(
                        user=request.user, poem_id=OuterRef("pk"))
                    ))
    else:
        qs = Poem.objects.all()
    if genre != "all":
        qs = qs.filter(genre__slug=genre)
    if author != "all":
        qs = qs.filter(author__slug=author)
    if search and search.strip() != "":
        qs = qs.filter(Q(author__name_hy__icontains=search) |
                       Q(author__name_ru__icontains=search) |
                       Q(author__name_en__icontains=search) |
                       Q(name_hy__icontains=search) |
                       Q(name_ru__icontains=search) |
                       Q(name_en__icontains=search) |
                       Q(content_hy__icontains=search) |
                       Q(content_en__icontains=search) |
                       Q(content_ru__icontains=search)).distinct()
    if request.user.is_authenticated:
        qs = qs.order_by('-want_to_read', '-favorite', 'name_hy')
    else:
        qs = qs.order_by('name_hy')
    paginator = Paginator(qs, per_page=12)
    page = request.GET.get('page', 1)
    try:
        poems = paginator.page(page)
    except PageNotAnInteger:
        poems = paginator.page(1)
    except EmptyPage:
        poems = paginator.page(paginator.num_pages)
    ctx = {
        "poems": poems,
        "selected_genre": genre,
        "selected_author": author,
        "search": search,
        "genres": Genre.objects.all().order_by('name_hy'),
        "authors": PoemAuthor.objects.all().order_by('name_hy'),
        'active': 'search'
    }
    if request.htmx:
        return render(request, 'core/partials/search-list.html', context=ctx)
    return render(request, 'core/search.html', context=ctx)


def photos(request):
    author = request.GET.get('author', "all")
    search = request.GET.get('search', "")
    qs = Photo.objects.filter(photos__writer__isnull=False).distinct()
    if author != "all":
        qs = qs.filter(photos__writer__slug=author)
    if search and search.strip() != "":
        qs = qs.filter(name__icontains=search)
    qs = qs.order_by('-id')
    paginator = Paginator(qs, per_page=15)
    page = request.GET.get('page', 1)
    try:
        photos = paginator.page(page)
    except PageNotAnInteger:
        photos = paginator.page(1)
    except EmptyPage:
        photos = paginator.page(paginator.num_pages)
    ctx = {
        "photos": photos,
        "selected_author": author,
        "search": search,
        "authors": PoemAuthor.objects.filter(
            photos__isnull=False).distinct().order_by('name_hy'),
        'active': 'photos'
    }
    if request.htmx:
        return render(request, 'core/partials/photo-list.html', context=ctx)
    return render(request, 'core/photos.html', context=ctx)


def photo(request, slug, id):
    photo = Photo.objects.get(id=id)
    writers = PoemAuthor.objects.filter(photos__photo_id=id)
    painters = GameAuthor.objects.filter(photos__photo_id=id)
    composers = AudioAuthor.objects.filter(photos__photo_id=id)
    if photo.slug != slug:
        return redirect(photo.main_url, permanent=True)
    ctx = {
        "writers": writers,
        "painters": painters,
        "composers": composers,
        "photo": photo,
        "poems": Poem.objects.filter(author__in=writers).order_by("?")[:15],
        "games": Game.objects.filter(author__in=painters).order_by("?")[:15],
        'active': 'photos'
    }
    return render(request, 'core/photo.html', context=ctx)


def remove_tags(request):
    for i in Poem.objects.filter(Q(content_hy__icontains="<a")
                                 | Q(content_hy__icontains="<table")):
        if i.content_hy:
            i.content_hy = no_tag(i.content_hy)
        if i.content_en:
            i.content_en = no_tag(i.content_en)
        if i.content_ru:
            i.content_ru = no_tag(i.content_ru)
        i.save()
    for i in AuthorBio.objects.all():
        if i.bio_hy:
            i.bio_hy = no_tag(i.bio_hy)
        if i.bio_en:
            i.bio_en = no_tag(i.bio_en)
        if i.bio_ru:
            i.bio_ru = no_tag(i.bio_ru)
        i.save()
    for i in AuthorQuote.objects.all():
        if i.bio_hy:
            i.bio_hy = no_tag(i.bio_hy)
        if i.bio_en:
            i.bio_en = no_tag(i.bio_en)
        if i.bio_ru:
            i.bio_ru = no_tag(i.bio_ru)
        i.save()
    return True
