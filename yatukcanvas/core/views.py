from django.shortcuts import render
from django.conf import settings
from django.utils.translation import check_for_language
from django.http import HttpResponseRedirect
from .models import (GameAuthor, Poem, Audio, Like, Favorite,
                     PoemComment, Photo, PoemAuthor, AudioAuthor, Game)
from .forms import ContactUsForm, GameCommentForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from utils.functions import send_yatuk_email
from django.utils.translation import activate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils.functions import check_user_login, no_tag
from django.db.models import Q
from django.utils.translation import get_language


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
        'most_populars': Game.objects.all().order_by('-played_count')[:15],
        "form": ContactUsForm(),
        "authors": GameAuthor.objects.filter(games__isnull=False).order_by("?").distinct()[:15],
        "carousel_items": Game.objects.all().order_by('?')[:15]
    }

    return render(request, 'core/index.html', context=ctx)


def authors(request):
    ctx = {
        "active": "authors",
        "authors": GameAuthor.objects.filter(games__isnull=False).order_by(f"name_{get_language()}").distinct()
    }
    return render(request, 'core/authors.html', context=ctx)


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


def author(request, slug):
    author = GameAuthor.objects.get(slug=slug)
    qs = Game.objects.filter(author=author).order_by(f'name_{get_language()}')
    paginator = Paginator(qs, per_page=12)
    page = request.GET.get('page', 1)
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        games = paginator.page(1)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)
    ctx = {
        "author": author,
        "games": games,
        'active': 'poems'
    }
    if request.htmx:
        return render(request, 'core/partials/game-list.html', context=ctx)
    return render(request, 'core/author.html', context=ctx)


def author_photoarchive(request, slug):
    author = GameAuthor.objects.get(slug=slug)
    photos = Photo.objects.filter(photos__painter_id=author.id).distinct()
    ctx = {
        "author": author,
        'photos': photos,
        'active': 'photoarchive'
    }
    if request.htmx:
        return render(request, 'core/partials/photoarchive.html', context=ctx)
    return render(request, 'core/author-photoarchive.html', context=ctx)


def game(request, author, slug, id):
    game = Game.objects.get(id=id)
    song = Audio.objects.all().order_by("?").first()
    poem_author = PoemAuthor.objects.all().order_by("?").first()
    game.played_count = 1 if not game.played_count else game.played_count + 1
    game.save()
    if request.user.is_authenticated:
        game.liked = game.likes.filter(user=request.user).exists()
        game.favorite = game.favorites.filter(user=request.user).exists()
    ctx = {
        "author": author,
        "game": game,
        "games": Game.objects.filter(author=game.author).exclude(id=game.id).order_by("?")[:10],
        'song': song,
        "poem_author": poem_author,
        "form": GameCommentForm(),
        "numbers": [25, 50, 100, 150, 200],
        'comments': PoemComment.objects.filter(game=game).order_by('-id')
    }
    return render(request, 'core/game.html', context=ctx)


def music(request):
    id = request.GET.get("id")
    song = Audio.objects.get(id=id)
    return render(request, 'core/partials/music-card.html', context={'song': song})


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
    game = Game.objects.get(id=id)
    check_user = check_user_login(request=request, next=game.main_url)
    if not check_user:
        return check_user
    like = Like.objects.filter(user=request.user, game_id=id)
    if like:
        like.delete()
        game.liked = False
    else:
        like = Like(user=request.user, game_id=id)
        like.save()
        game.liked = True
    game.favorite = game.favorites.filter(user=request.user).exists()
    return render(request, 'core/partials/like.html', context={'game': game})


def favorite(request, id):
    game = Game.objects.get(id=id)
    check_user = check_user_login(request=request, next=game.main_url)
    if not check_user:
        return check_user
    favorite = Favorite.objects.filter(user=request.user, game_id=id)
    if favorite:
        favorite.delete()
        game.favorite = False
    else:
        favorite = Favorite(user=request.user, game_id=id)
        favorite.save()
        game.favorite = True
    game.liked = game.likes.filter(user=request.user).exists()
    return render(request, 'core/partials/like.html', context={'game': game})


@login_required
def saved(request):
    qs = Game.objects.filter(favorites__user=request.user)
    qs = qs.order_by('name_hy')
    paginator = Paginator(qs, per_page=12)
    page = request.GET.get('page', 1)
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        games = paginator.page(1)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)
    ctx = {
        "games": games,
    }
    if request.htmx:
        return render(request, 'core/partials/saved-game-list.html', context=ctx)
    return render(request, 'core/saved.html', context=ctx)


def comment(request, id):
    if request.method == 'POST':
        game = Game.objects.get(id=id)
        check_user = check_user_login(request=request, next=game.main_url)
        if not check_user:
            return check_user
        form = GameCommentForm(request.POST)
        if form.is_valid():
            comment = PoemComment(text=form.cleaned_data['text'],
                                  user=request.user,
                                  game=game)
            comment.save()
            ctx = {
                'form': GameCommentForm(),
                'game': game,
                'comments': PoemComment.objects.filter(game=game).order_by('-id')
            }
            return render(request, 'core/partials/comment-form.html', ctx)
        ctx = {
            'form': GameCommentForm(request.POST),
            'game': game,
            'comments': PoemComment.objects.filter(game=game).order_by('-id')
        }
        return render(request, 'core/partials/comment-form.html', ctx)


def search(request):
    author = request.GET.get('author', "all")
    search = request.GET.get('search', "")
    qs = Game.objects.all()
    if author != "all":
        qs = qs.filter(author__slug=author)
    if search and search.strip() != "":
        qs = qs.filter(Q(name_hy__icontains=search) |
                    Q(name_ru__icontains=search) |
                    Q(name_en__icontains=search) |
                    Q(author__name_hy__icontains=search) |
                    Q(author__name_ru__icontains=search) |
                    Q(author__name_en__icontains=search)).distinct()
    qs = qs.order_by('name_hy')
    paginator = Paginator(qs, per_page=12)
    page = request.GET.get('page', 1)
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        games = paginator.page(1)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)
    ctx = {
        "games": games,
        "selected_author": author,
        "search": search,
        "authors": GameAuthor.objects.all().order_by('name_hy'),
        'active': 'search'
    }
    if request.htmx:
        return render(request, 'core/partials/search-list.html', context=ctx)
    return render(request, 'core/search.html', context=ctx)


def photos(request):
    author = request.GET.get('author', "all")
    search = request.GET.get('search', "")
    qs = Photo.objects.filter(photos__painter_id__isnull=False).distinct()
    if author != "all":
        qs = qs.filter(photos__painter__slug=author)
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
        "authors": GameAuthor.objects.filter(photos__isnull=False).distinct().order_by('name_hy'),
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
    for i in Poem.objects.filter(Q(content_hy__icontains="<a") | Q(content_hy__icontains="<table")):
        if i.content_hy:
            i.content_hy = no_tag(i.content_hy)
        if i.content_en:
            i.content_en = no_tag(i.content_en)
        if i.content_ru:
            i.content_ru = no_tag(i.content_ru)
        i.save()
    return True


def get_game(request, id):
    game = Game.objects.get(id=id)
    size = int(request.GET.get('size', 25))
    # game.played_count = game.played_count+1 if game.played_count else 1
    # game.save()
    src = f"https://www.jigsawplanet.com/?rc=play&pid={game.pid}&view="
    src += f"iframe&bgcolor=0x{game.main_color}&savegame=0&pieces={size}"
    ctx = {
        'game': game,
        'shapes': range(0, 8),
        'sizes': [25, 50, 75, 100, 125, 150, 175, 200],
        'size': size,
        'src': src
    }
    return render(request, 'core/partials/game-iframe.html', context=ctx)
