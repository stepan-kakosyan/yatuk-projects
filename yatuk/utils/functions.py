import string
from django.utils.text import slugify
import random
from PIL import Image
from django.core.mail import send_mail

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
            r, g, b = img.getpixel((x,y))
            r_total += r
            g_total += g
            b_total += b
            count += 1
    return '%02x%02x%02x' % (int(r_total/count), int(g_total/count), int(b_total/count))

def send_yatuk_email(subject, from_, to_, message, html):
    msg = send_mail(subject=subject,
                  message=message,
                  html_message = html,
                  from_email=from_,
                  recipient_list=to_)
    return msg
