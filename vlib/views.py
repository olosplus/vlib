# coding : utf-8
from django.http import HttpResponse
import json
from django.db.models import get_model
from django.apps import apps
from django.core.exceptions import ValidationError

def insert(data, model):
    lista = data.split("|")    
    for row in lista:        
        row_json = dict(json.loads(row))
        mod = model()
        for field in model._meta.fields:
            if field.name == 'id':
                continue
            if field.name in row_json:
                setattr(mod, field.name, row_json[field.name])
            else:
                if field.name + '_id' in row_json:
                    setattr(mod, field.name + '_id', row_json[field.name + '_id'])
        try:
            mod.full_clean()
        except ValidationError as e:
            return e
        mod.save()        
    return ""    

def delete(data, model):
    lista = data.split("|")    
    for row in lista:        
        row_json = dict(json.loads(row))
        mod = model.objects.get(pk=row_json['id'])
        try:
            mod.delete()
        except Error as e:
            return e
        
    return ""    


def update(data, model):
    lista = data.split("|")    
    for row in lista:        
        row_json = dict(json.loads(row))
        mod = model.objects.get(pk=row_json['id'])
        for field in model._meta.fields:
            if field.name == 'id':
                continue
            if field.name in row_json:
                setattr(mod, field.name, row_json[field.name])
            else:
                if field.name + '_id' in row_json:
                    setattr(mod, field.name + '_id', row_json[field.name + '_id'])
        try:
            mod.full_clean()
        except ValidationError as e:
            return e
        mod.save()        
    return ""    

def save_grid(request):    
    str_model = request.GET.get('model')
    str_module = request.GET.get('module')
    list_module = str_module.split('.')    
    try:
        model = apps.get_app_config(list_module[len(list_module)-2]).get_model(str_model)
    except LookupError:
        return HttpResponse("An error ocurred. The model or module don't exists")


    data = request.GET.get('rows_inserted')
    if data:
        erro = insert(data, model)
        if erro:
            return HttpResponse(erro)
  
    data = request.GET.get('rows_updated')
    if data:
        erro = update(data, model)
        if erro:
            return HttpResponse(erro)
 
    return HttpResponse('Dados atualizados com sucesso!');



def delete_grid(request):    
    str_model = request.GET.get('model')
    str_module = request.GET.get('module')
    list_module = str_module.split('.')    
    try:
        model = apps.get_app_config(list_module[len(list_module)-2]).get_model(str_model)
    except LookupError:
        return HttpResponse("An error ocurred. The model or module don't exists")


    data = request.GET.get('rows_deleted')
    if data:
        erro = delete(data, model)
        if erro:
            return HttpResponse(erro)
 
    return HttpResponse('Dados atualizados com sucesso!');
