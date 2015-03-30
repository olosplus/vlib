from django import template
from django.core.urlresolvers import resolve
from django.core.handlers.wsgi import WSGIRequest
from vlib import config
from django.apps import apps

register = template.Library()
@register.assignment_tag(takes_context=True)
def get_info_app_name(context, request):   
    return apps.get_app_config('admin').verbose_name

@register.filter(name='get_info')
def get_info(valor, info):
    valor = getattr(config.Config, info)
    return valor
