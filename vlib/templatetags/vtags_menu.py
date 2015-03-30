from django import template
from django.conf import settings
from django.apps import apps as apps_on_project
import os.path
from vlib import menu_apps

DIR = settings.BASE_DIR
TAG_DROP = "<span class='fa arrow'></span>"
TAG_UL_SEC = "<ul class='nav nav-second-level'>"
TAG_UL_THI = "<ul class='nav nav-third-level'>"
TAG_UL = "<ul>"
TAG_LI = "<li>"
CLOSE_TAG_LI = "</li>"
TAG_I = "<i "
CLOSE_TAG_I = "</i>"
CLOSE_TAG_UL = "</ul>"
TAG_A_PARTIAL = "<a"
TAG_A = "<a>"
CLOSE_TAG_A = "</a>"
ATTR_HREF = "href="
CLOSE_TAG = ">"
OPEN_TAG = "<"

def has_model(directory):
    """Verifica se há o arquivo models.py no diretório informado"""
    return os.path.isfile(directory + '/models.py')

def has_url(directory):
    """Verifica se há o arquivo urls.py no diretório informado"""
    return os.path.isfile(directory + '/urls.py')

def load_urls_patterns(patterns):
    """Retorna a lista de configurações das urls do patterns passado no parâmetro"""
    URL_NAMES = []
    for pat in patterns:
        if pat.__class__.__name__ == 'RegexURLPattern':
            URL_NAMES.append(pat.regex.pattern)
    return URL_NAMES

def get_app_name_on_path(path):
    position_path_app = len(DIR) + 1
    tree_app = ''.join(path[position_path_app:])
    tree_app = tree_app.replace("/", ".")
    return tree_app

def module_exists(module_name):
    try:
        __import__(module_name, fromlist = ['no_module_list'])
    except ImportError:
        return False
    else:
        return True        

def load_url_app(path_app):
    """Retorna a primeira url da lista de urls configuradas para o app situado no diretório 
       completo informado no parâmetro
    """
    if not has_url(path_app):
        return "javascript:void(0)"
    tree_app = get_app_name_on_path(path_app) #tree_app.replace("/", ".")
    urls = []
    app = __import__(tree_app, fromlist=['no_module_list'])    
    if app:
        if hasattr(app, 'urls'):
            if app.urls.urlpatterns:        
                urls = load_urls_patterns(app.urls.urlpatterns)                
    if urls:
        return  "/" + urls[0].split('.')[0].replace("^", "")
    else:  
        return "javascript:void(0)"

def installed_apps():
    """ Retorna a lista com o nome do app. Apenas o nome, não retorna a árvore de módulos completa"""
    lapps = []
    for app in settings.INSTALLED_APPS  :
        for nome_app in app.split("."):
            lapps.append(nome_app)
        else:
            lapps.append(app)
    return lapps

NAME_APPS_INSTALLED = installed_apps() 
def get_apps_html(path, hab_UL=False, nivel=1):
    """ monta o html do menu"""
    html = ""
    abrir_ul = False
    url_app = ""
    if os.path.isdir(path):
        try:
            dirs = next(os.walk(path))[1]
            dirs.sort()
        except PermissionError:
            dirs = []
        for directory in dirs:
            #return bool_apps_filho(directory)
            app_name = get_app_name_on_path(path + "/" + directory)
            if directory in NAME_APPS_INSTALLED:
                if not menu_apps.MenuApps.AppIsVisible(app_name):
                    continue
            
                if hab_UL:
                    if not abrir_ul:
                        nivel+=1
                        if nivel == 2:
                           html += TAG_UL_SEC
                        else:
                           html += TAG_UL_THI
                        abrir_ul = True
                
                if html:
                    html += TAG_LI

                url_app = load_url_app(path + "/" + directory)
                html += "%s %s '%s' %s" % (TAG_A_PARTIAL, ATTR_HREF, url_app, CLOSE_TAG)
                if menu_apps.MenuApps.ImgMenuApp(app_name):
                    html += "%s class='%s'> %s" % (TAG_I, menu_apps.MenuApps.ImgMenuApp(app_name),CLOSE_TAG_I)
                html += ' '+menu_apps.MenuApps.GetAppVerboseName(app_name)
                if bool_apps_filho(path + "/" + directory):
                    html += TAG_DROP
                html += CLOSE_TAG_A
                html += get_apps_html(path + "/" + directory, True, nivel)
                
                if html:
                    html += CLOSE_TAG_LI
        if abrir_ul:
            html += CLOSE_TAG_UL
            nivel-=1
    return html  

LIST_APPS_MENUS = menu_apps.MenuApps.GetAppsOnMenu()

def bool_apps_filho(path_app):
    """ verifica se aplicacao tem filho"""
    
    dirs = next(os.walk(path_app))[1]
    for directory in dirs:
        tree_app = get_app_name_on_path(path_app + "/"+ directory)

        if tree_app in LIST_APPS_MENUS:
#            if menu_apps.MenuApps.AppIsVisible(tree_app):
            return True
    return False

register = template.Library()
@register.assignment_tag(takes_context=True)
def get_menu(context, request):
    """Retorna o html do menu(uma lista)"""
    return get_apps_html(DIR)