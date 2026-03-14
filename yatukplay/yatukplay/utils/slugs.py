import string
from django.utils.text import slugify
import random


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name_en.lower(), allow_unicode=True)
    cl = instance.__class__
    qs_exists = cl.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = f"{slug}-{random_string_generator(size = 2)}"
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug