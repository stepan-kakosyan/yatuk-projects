from django import template
from django.template import Library
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.filter
def replace_space(value):
    return value.replace("&nbsp;", "").replace('&mdash;', ' ')

MONTHS = {
    1: _("January"),
    2: _("February"), 
    3: _("March"), 
    4: _("April"),
    5: _("May"),  
    6: _("June"),  
    7: _("July"),  
    8: _("August"),
    9: _("September"),  
    10: _("October"), 
    11: _("November"),
    12: _("December"),
 }
 
register = Library()

@register.filter(name='beauty_date')
def beauty_date(date):
    return f"{date.day} {MONTHS[date.month]} {date.year}"

@register.filter(name='beauty_price')
def beauty_price(arg):
    return f"{arg} ֏"