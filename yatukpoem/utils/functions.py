import string
from django.utils.text import slugify
import random
from PIL import Image
from django.core.mail import send_mail
from django.shortcuts import resolve_url
from django.http import HttpResponse
from yatukpoem import settings
from django.shortcuts import redirect
from django.utils.translation import get_language


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(str(instance.name_en)[:30].lower(), allow_unicode=True)
    cl = instance.__class__
    qs_exists = cl.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = f"{slug}-{random_string_generator(size = 2)}"
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def compute_average_image_color(self):
    img = Image.open(self.image)
    width, height = img.size
    r_total = 0
    g_total = 0
    b_total = 0
    count = 0
    for x in range(0, width):
        for y in range(0, height):
            r, g, b = img.getpixel((x, y))
            r_total += r
            g_total += g
            b_total += b
            count += 1
    return '%02x%02x%02x' % (int(r_total/count), int(g_total/count), int(b_total/count))


def send_yatuk_email(subject, from_, to_, message, html):
    msg = send_mail(subject=subject,
                    message=message,
                    html_message=html,
                    from_email=from_,
                    recipient_list=to_)
    return msg


def check_user_login(request, next):
    if not request.user.is_authenticated:
        rurl = resolve_url(settings.LOGIN_URL)
        resolved_login_url = f"/{get_language()}{rurl}?next={next}"
        if request.htmx:
            response = HttpResponse(status=204, headers={'HX-Redirect': resolved_login_url})
            return response
        else:
            return redirect(resolved_login_url)
    else:
        return True


def no_tag(text):
    text = text.strip().replace("&nbsp;", " ").replace('&mdash;', ' ')
    a_tag_start = text.split('<a')
    removable_texts = []
    if len(a_tag_start) > 1:
        for i in a_tag_start[1:]:
            _a = i.split('>')[0]
            replace_text = f"<a{_a}>"
            removable_texts.append(replace_text)
        removable_texts.append("</a>")
    table_tag_start = text.split('<table')
    if len(table_tag_start) > 1:
        for i in table_tag_start[1:]:
            _t = i.split('>')[0]
            replace_text = f"<table{_t}>"
            removable_texts.append(replace_text)
        removable_texts.append("</table>")
    bracket_start = text.split('[')
    if len(bracket_start) > 1:
        for i in bracket_start[1:]:
            _b = i.split(']')[0]
            replace_text = f"[{_b}]"
            removable_texts.append(replace_text)
    rem_texts = list(set(removable_texts) | set(['<thbody>', '<tr>', '<td>',
                                                 '</thbody>', '</tr>', '</td>']))
    for i in rem_texts:
        text = text.replace(i, "")
    return text
