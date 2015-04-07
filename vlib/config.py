# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import resolve
from django.core.handlers.wsgi import WSGIRequest

class Config:
    PROJECT_NAME = "V-Commerce"
    PROJECT_VERSION = "Versão: 0.0.0.1"
    #USER_ID = User