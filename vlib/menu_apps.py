# coding: utf-8
from django.conf.urls import patterns, include, url
import os 
from django.db import models

models.options.DEFAULT_NAMES += ('child_models',)

DIR = os.path.dirname(os.path.dirname(__file__))

MAIN_APP = {'app': 'home', 'verbose_name': 'Home', 'view_name': 'home.views.index' }

apps_on_menu = (
    {'app': 'cadastro', 'verbose_name' : 'Cadastro', 'imgmenu':'fa fa-sitemap'},
    {'app': 'cadastro.almoxarifado', 'verbose_name' : 'Almoxarifado'},
    {'app': 'cadastro.cliente', 'verbose_name' : 'Cliente'},
    {'app': 'cadastro.contato', 'verbose_name' : 'Contato', 'visible': False},
    {'app': 'cadastro.empresa', 'verbose_name' : 'Empresa'},
    {'app': 'cadastro.fornecedor', 'verbose_name' : 'Fornecedor'},
    {'app': 'cadastro.localidade', 'verbose_name' : 'Localidades', },
    {'app': 'cadastro.localidade.bairro', 'verbose_name' : 'Bairro'},
    {'app': 'cadastro.localidade.cidade', 'verbose_name' : 'Cidade'},
    {'app': 'cadastro.localidade.estado', 'verbose_name' : 'Estado'},
    {'app': 'cadastro.localidade.pais', 'verbose_name' : 'Países'},
    {'app': 'cadastro.produto', 'verbose_name' : 'Produto'},
    {'app': 'cadastro.produto.item', 'verbose_name' : 'Produto'},
    #{'app': 'cadastro.produto.localizacao', 'verbose_name' : 'Localização'},
    {'app': 'cadastro.produto.unimedida', 'verbose_name' : 'Unidade de Medida'},
    {'app': 'cadastro.unidade', 'verbose_name' : 'Unidade'},
    {'app': 'cadastro.funcionario', 'verbose_name' : 'Funcionário'},
)

class MenuApps:       
    @staticmethod
    def GetAppsOnMenu():
        apps = ()
        for app in apps_on_menu:
            apps += (app['app'], )
        return apps

    @staticmethod
    def IncludeUrls():
        patt = patterns('', url(r'^$', MAIN_APP['view_name']),)
        for app in apps_on_menu:
            if os.path.isfile(DIR + "/" + app['app'].replace(".", "/") + "/urls.py"):
                patt += patterns('', url(r'', include(app['app'] + '.urls')),)
        return patt
   
    @staticmethod
    def GetAppVerboseName(app_name):
        for app in apps_on_menu:
            if app['app'].upper() == app_name.upper():
           	    return app['verbose_name']
    @staticmethod
    def AppIsVisible(app_name):
        for app in apps_on_menu:            
            if app['app'].upper() == app_name.upper():                
                if 'visible' in app:
                    return app['visible']
                else:
                    return True

    @staticmethod
    def ImgMenuApp(app_name):
        for app in apps_on_menu:
            if app['app'].upper() == app_name.upper():
                if 'imgmenu' in app:
                    return app['imgmenu']
                else:
                    return ''
