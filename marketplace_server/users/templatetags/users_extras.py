import datetime

from django import template
from django.utils import timezone
from django.utils.timesince import timesince

register = template.Library()


@register.filter
def humanize_date(value: datetime) -> str:
    now = timezone.now()

    if value.day == now.day:
        return "сегодня"
    elif value.day == now.day - 1:
        return "вчера"
    return f"{timesince(value).split(', ')[0]} назад"
