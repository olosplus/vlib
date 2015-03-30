# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.core import serializers
from vlib.url_lib import urlsCrud
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.forms import models
from django.db import models as modeldb
from django.core.exceptions import ValidationError
#from django.db.models import ForeignKey
from vlib.grid import Grid
#CONSTS
TEMPLATE_INSERT = '_insert_form.html'
TEMPLATE_UPDATE = '_update_form.html'
TEMPLATE_DELETE = '_delete_form.html'
TEMPLATE_LIST = '_list_form.html'

DOT_CSS = '.CSS'
DOT_JAVA_SCRIPT = '.JS'

#To set temporary model 
class EmptyClass(modeldb.Model):
   pass

class StaticFiles:  
    @staticmethod
    def GetSameTypeFiles(ListOfFiles, Extension):
        files = []       
        for media in ListOfFiles:
            if media[media.index('.'):].upper() == Extension.upper():
                files.append(media)    
        return tuple(files)

    @staticmethod
    def GetCss(ListOfFiles):
        return StaticFiles.GetSameTypeFiles(ListOfFiles = ListOfFiles, Extension = DOT_CSS)

    @staticmethod
    def GetJs(ListOfFiles):
        return StaticFiles.GetSameTypeFiles(ListOfFiles = ListOfFiles, Extension = DOT_JAVA_SCRIPT)

class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response

class ViewCreate(AjaxableResponseMixin, CreateView):  
    template_name = TEMPLATE_INSERT
    MediaFiles = []   

    def get_success_url(self):
        return self.success_url

    @method_decorator(login_required)  
    def dispatch(self, *args, **kwargs):
        return super(ViewCreate, self).dispatch(*args, **kwargs)

    def __init__(self, **kwargs):
        if 'MediaFiles' in kwargs :
            self.MediaFiles = kwargs.get('MediaFiles')
        super(ViewCreate, self).__init__(**kwargs)


    def get_context_data(self, **kwargs):   
        Urls = urlsCrud(self.model);
        grid = Grid(self.model)
        context = super(ViewCreate, self).get_context_data(**kwargs)   
        context['JsFiles'] = StaticFiles.GetJs(self.MediaFiles)
        context['CssFiles'] = StaticFiles.GetCss(self.MediaFiles)
        context['url_list'] =  Urls.BaseUrlList(CountPageBack = 1)    
        context['url_insert'] = Urls.BaseUrlInsert(1)
        context['form_id'] = self.model.__name__
        context['grid'] = grid.grid_as_text(use_crud = False, read_only = False);        
        return context
 
class ViewUpdate(UpdateView):
    template_name = TEMPLATE_UPDATE
    MediaFiles = []
    def __init__(self, **kwargs):
        if 'MediaFiles' in kwargs :
            self.MediaFiles = kwargs.get('MediaFiles')
        super(ViewUpdate, self).__init__(**kwargs)

    def get_context_data(self, **kwargs):   
        Urls = urlsCrud(self.model);    
        context = super(UpdateView, self).get_context_data(**kwargs)   
        context['JsFiles'] = StaticFiles.GetJs(self.MediaFiles)
        context['CssFiles'] = StaticFiles.GetCss(self.MediaFiles)    
        context['url_list'] =  Urls.BaseUrlList(CountPageBack = 1)    
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ViewUpdate, self).dispatch(*args, **kwargs)

class ViewDelete(DeleteView):
    template_name = TEMPLATE_DELETE
    MediaFiles = []

    @method_decorator(login_required)  
    def dispatch(self, *args, **kwargs):
        return super(ViewDelete, self).dispatch(*args, **kwargs)

    def __init__(self, **kwargs):
        if 'MediaFiles' in kwargs :
            self.MediaFiles = kwargs.get('MediaFiles')
        super(ViewDelete, self).__init__(**kwargs)

    def get_context_data(self, **kwargs):   
        Urls = urlsCrud(self.model);
        context = super(ViewDelete, self).get_context_data(**kwargs)   
        context['JsFiles'] = StaticFiles.GetJs(self.MediaFiles)
        context['CssFiles'] = StaticFiles.GetCss(self.MediaFiles)    
        context['url_list'] =  Urls.BaseUrlList(CountPageBack = 1)        
        return context

class ViewList(ListView):
    template_name = TEMPLATE_LIST
    MediaFiles = []
    Grid_Fields =()
    def __init__(self, **kwargs):
        if 'MediaFiles' in kwargs :
            self.MediaFiles = kwargs.get('MediaFiles')
        if 'Grid_Field' in kwargs :
            self.Grid_Fields = kwargs.get('Grid_Fields')
        super(ViewList, self).__init__(**kwargs)

    
    def get_context_data(self, **kwargs):   

        context = super(ViewList, self).get_context_data(**kwargs)   
        
        grid = Grid(self.model)
       
        context['JsFiles'] = StaticFiles.GetJs(self.MediaFiles)
        context['CssFiles'] = StaticFiles.GetCss(self.MediaFiles)  
        context['grid'] = grid.grid_as_text(display_fields = self.Grid_Fields, use_crud = True, read_only = True);

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ViewList, self).dispatch(*args, **kwargs)

class ConvertView:
    def __init__(self, model):
        self.model = model
        self.Urls = urlsCrud(model);  

    def Update(self, MediaFiles = [],  ClassView = ViewUpdate):
        return ClassView.as_view(model = self.model, success_url = self.Urls.BaseUrlList(CountPageBack=2), 
            template_name = TEMPLATE_UPDATE, MediaFiles = MediaFiles)

    def Create(self, MediaFiles = [], ClassView = ViewCreate):    
        return ClassView.as_view(model = self.model, success_url = self.Urls.BaseUrlList(CountPageBack=2), 
            template_name = TEMPLATE_INSERT, MediaFiles = MediaFiles)    

    def Delete(self, MediaFiles = [], ClassView = ViewDelete):
        return ClassView.as_view(model = self.model, success_url = self.Urls.BaseUrlList(CountPageBack=2), 
            template_name = TEMPLATE_DELETE, MediaFiles = MediaFiles)        

    def List(self, MediaFiles = [], Grid_Fields = [], ClassView = ViewList):
        return ClassView.as_view(model = self.model, template_name = TEMPLATE_LIST, MediaFiles = MediaFiles,
        Grid_Fields = Grid_Fields)

class CrudView:
    def __init__(self, model):
        self.model = model
        self.view = ConvertView(model)
        self.UrlCrud = urlsCrud(model);

    def AsUrl(self, MediaFilesInsert = [], MediaFilesUpdate = [], MediaFilesDelete = [], MediaFilesList = [], 
        GridFields = (), ClassCreate = ViewCreate, ClassUpdate = ViewUpdate, ClassDelete = ViewDelete, 
        ClassList = ViewList):
        urls = patterns('', 
            url(self.UrlCrud.UrlList(), self.view.List(MediaFiles = MediaFilesList, Grid_Fields = GridFields,
                ClassView = ClassList)),
            url(self.UrlCrud.UrlInsert(), self.view.Create(MediaFiles = MediaFilesInsert, ClassView = ClassCreate )), 
            url(self.UrlCrud.UrlUpdate(), self.view.Update(MediaFiles = MediaFilesUpdate, ClassView = ClassUpdate)),
            url(self.UrlCrud.UrlDelete(), self.view.Delete(MediaFiles = MediaFilesDelete, ClassView = ClassDelete)))
        return urls 
