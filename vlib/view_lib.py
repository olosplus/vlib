# -*- coding: utf-8 -*-
import json
from django.shortcuts import render_to_response
from django import forms
from django.http import HttpResponse
from django.http import HttpResponseRedirect
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
from django.core.exceptions import ValidationError, ObjectDoesNotExist 
from vlib.grid import Grid
from django.forms import ModelForm, Form
from vlib import views as vlib_views
from django.forms.utils import ErrorList

try:
    from cadastro.funcionario.models import Funcionario
    UtilizaFuncionario = True
except ImportError:
    UtilizaFuncionario = False

#CONSTS
TEMPLATE_INSERT = '_insert_form.html'
TEMPLATE_UPDATE = '_update_form.html'
TEMPLATE_DELETE = '_delete_form.html'
TEMPLATE_LIST = '_list_form.html'
GRID_SEPARATOR = "[[<<ROW_SEPARATOR>>]]"
DOT_CSS = '.CSS'
DOT_JAVA_SCRIPT = '.JS'

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
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }

            return JsonResponse(data)
        else:
            return response

class StandardFormGrid(ModelForm):
    child_models = str()
    current_user = None
    def split_child_models(self):        
        return self.child_models.split(GRID_SEPARATOR)
                     
    def get_grids_erros(self):        
        erro = ""
        if self.child_models:
            grids = self.split_child_models()

            for grid in grids:
                if not grid:
                    continue                
                data_dict = json.loads(grid)                

                if not 'rows_inserted' in data_dict:
                    continue

                model = vlib_views.get_model_by_string(data_dict['module'], data_dict['model'])
     
                if data_dict['rows_inserted']:
                    erro = vlib_views.insert(data = data_dict['rows_inserted'], model = model, commit = False,
                        link_to_form = data_dict['link_to_form'])                                 
                if erro:
                    return erro
                else:
                    if data_dict['rows_updated']:
                        erro = vlib_views.update(data = data_dict['rows_updated'], model = model, commit = False)
                    if erro:
                        return erro
        return str()

    def custom_grid_validations(self, grid_model, grid_data, parent_instance):
        '''override this method to make custom validations'''
        return ""

    def save_grids(self, parent_instance_pk):        
        erro = ""
        if self.child_models:            
            grids = self.split_child_models()
            for grid in grids:
                if not grid:
                    continue                    
 
                data_dict = json.loads(grid)        
                model = vlib_views.get_model_by_string(data_dict['module'], data_dict['model'])

                erro = self.custom_grid_validations(grid_model = model, grid_data = data_dict, \
                 parent_instance = parent_instance_pk)

                if erro:
                    return erro

                if 'rows_deleted' in data_dict:                    
                    if data_dict['rows_deleted']:
                        return vlib_views.delete(data = data_dict['rows_deleted'], model = model)                                  
                else:
                    if data_dict['rows_inserted']:                    
                        erro = vlib_views.insert(data = data_dict['rows_inserted'], model = model, commit = True,
                            link_to_form = data_dict['link_to_form'], parent_instance = parent_instance_pk) 
                    if erro:
                        return erro
    
                    if data_dict['rows_updated']:                        
                        erro = vlib_views.update(data = data_dict['rows_updated'], model = model, commit = True)
                        return erro
        return str()        

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
            initial=None, error_class=ErrorList, label_suffix=None,
            empty_permitted=False, instance=None):
        
        if data:
            copy_data = data.copy()
            if 'empresa' in data and UtilizaFuncionario: 
                try:
                    func = Funcionario.objects.get(user = self.current_user)            
                except ObjectDoesNotExist :
                    func = None
                if func != None:
                    copy_data['empresa'] = func.empresa.id
        else:
            copy_data = None    

        super(StandardFormGrid, self).__init__(data=copy_data, files=files, auto_id=auto_id, prefix=prefix,
            initial= initial, error_class=error_class, label_suffix=label_suffix,
            empty_permitted=empty_permitted, instance=instance)

    def save(self, commit = False):
        instance = super(StandardFormGrid, self).save(commit=True)                
        erro = self.save_grids(parent_instance_pk = instance)                        
        if erro:
            return HttpResponse(erro)

        return instance    

class CreateForm(object):
    def __init__(self, model):
        self.model = model

    def create_form(self, class_form = StandardFormGrid, GridsData = "", user = None):
        class vmsisForm(class_form):                    
            class Meta:
                model = self.model                                
            child_models = GridsData
            current_user = user
        return vmsisForm
   
class ViewCreate(CreateView, AjaxableResponseMixin):  
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
    
    def post(self, request, *args, **kwargs):        
        grids_data = request.POST['child_models']
        
        if self.form_class == None:
            self.form_class = StandardFormGrid
        self.form_class = CreateForm(self.model).create_form(GridsData = grids_data, class_form = self.form_class, \
            user = request.user)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        self.object = self.model

        grid_erros =  form.get_grids_erros()
        
        if grid_erros:
            return HttpResponse(grid_erros) 

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


    def get_context_data(self, **kwargs):   
        Urls = urlsCrud(self.model);
        grid = Grid(self.model)
        context = super(ViewCreate, self).get_context_data(**kwargs)   
        context['JsFiles'] = StaticFiles.GetJs(self.MediaFiles)
        context['CssFiles'] = StaticFiles.GetCss(self.MediaFiles)
        context['url_list'] =  Urls.BaseUrlList(CountPageBack = 1)    
        context['url_insert'] = Urls.BaseUrlInsert(1)
        context['form_id'] = self.model.__name__
        context['grid'] = grid.grid_as_text(use_crud = False, read_only = False, dict_filter = {'id':-1});        
        return context
 
class ViewUpdate(UpdateView, AjaxableResponseMixin):
    template_name = TEMPLATE_UPDATE
    MediaFiles = []

    def __init__(self, **kwargs):
        if 'MediaFiles' in kwargs :
            self.MediaFiles = kwargs.get('MediaFiles')
        super(ViewUpdate, self).__init__(**kwargs)
    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):   
        Urls = urlsCrud(self.model);            
        context = super(UpdateView, self).get_context_data(**kwargs)   
        context['form_id'] = self.model.__name__        
        objeto =  context['object']
        grid = Grid(model = self.model, parent_pk_value = objeto.pk)
        context['grid'] = grid.grid_as_text(use_crud = False, read_only = False);
        context['form_pk'] = objeto.pk
        context['JsFiles'] = StaticFiles.GetJs(self.MediaFiles)
        context['CssFiles'] = StaticFiles.GetCss(self.MediaFiles)    
        context['url_list'] =  Urls.BaseUrlList(CountPageBack = 1)    
        context['url_update'] = Urls.BaseUrlUpdate(CountPageBack = 1)        
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ViewUpdate, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        grids_data = request.POST['child_models']
        if self.form_class == None:
            self.form_class = StandardFormGrid
        self.form_class = CreateForm(self.model).create_form(GridsData = grids_data, class_form = self.form_class, \
            user = request.user)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        self.object = self.model        
        grid_erros =  form.get_grids_erros()

        if grid_erros:
            return HttpResponse(grid_erros)

        return  super(ViewUpdate, self).post(request, *args, **kwargs)        
        
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
        context['url_list'] = Urls.BaseUrlList(CountPageBack = 1)        
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
