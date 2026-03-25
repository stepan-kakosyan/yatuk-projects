from django.shortcuts import render
from django.db.models import Q
import json
from django.db import models
from django.db.models import Func
from django.conf import settings
from django.utils.translation import check_for_language, get_language
from django.http import HttpResponseRedirect
from .serializers import AudioSerializer
from .models import Audio, Author, Product
from django.views.decorators.csrf import csrf_exempt


class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()


def set_language(request):
    from django.utils.translation import activate
    lang_code = request.GET.get('language', settings.LANGUAGE_CODE)
    next_url = "/"+lang_code+"/"
    response = HttpResponseRedirect(next_url)
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['language'] = lang_code
        response.set_cookie("django_language", lang_code, max_age=31536000)
        request.session.set_expiry(31536000)
        activate(lang_code)
    return response


def index(request, author=None, slug=None):
    audios = Audio.objects.all().order_by("?")
    if slug:
        first_song = audios.filter(slug=slug)
        audios = audios.exclude(slug=slug)
        result = first_song.union(audios)
        first_song_ = first_song.first()
    else:
        first_song_ = None
        result = audios
    ctx = {
        'audios': result,
        "slug": slug,
        "first_song": first_song_,
        'audios_json': json.dumps(AudioSerializer(result, many=True).data),
        'products': Product.objects.all().order_by("?")[:5]
    }
    return render(request, 'core/index.html', context=ctx)


@csrf_exempt
def author_info(request, id):
    song = Audio.objects.get(id=id)
    song.played_count = song.played_count+1 if song.played_count else 1
    song.save()
    ctx = {
        'author': song.author,
        'song_slug': song.slug
    }
    return render(request, 'core/partials/author.html', context=ctx)


@csrf_exempt
def get_author_songs(request, id):
    ctx = {
        'author': Author.objects.get(id=id),
        'songs': Audio.objects.filter(author_id=id).order_by(f"name_{get_language()}"),
        'current_song': int(request.GET.get("current_song"))
    }
    return render(request, 'core/partials/songs.html', context=ctx)


@csrf_exempt
def get_author_info(request, id):
    ctx = {
        'author': Author.objects.get(id=id),
    }
    return render(request, 'core/partials/author.html', context=ctx)


@csrf_exempt
def authors(request):
    ctx = {
        'authors': Author.objects.all().order_by(f"name_{get_language()}")
    }
    return render(request, 'core/partials/authors.html', context=ctx)


@csrf_exempt
def songs(request):
    ctx = {
        'songs': Audio.objects.all().order_by(f"name_{get_language()}")
    }
    return render(request, 'core/partials/all-songs.html', context=ctx)


@csrf_exempt
def search(request):
    search = request.GET.get('search', None)
    ctx = {}
    if search is not None and search != "":
        query = Q(Q(name_en__icontains=search) | Q(name_hy__icontains=search) | Q(name_ru__icontains=search))
        ctx['songs'] = Audio.objects.filter(query).order_by(f"name_{get_language()}")
        ctx['authors'] = Author.objects.filter(query).order_by(f"name_{get_language()}")
        ctx['show_message'] = True
        return render(request, 'core/partials/search-result.html', context=ctx)
    elif search == "":
        ctx['show_message'] = False
        return render(request, 'core/partials/search-result.html', context=ctx)
    return render(request, 'core/partials/search.html', context=ctx)
