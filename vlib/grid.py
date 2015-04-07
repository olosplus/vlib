# coding: utf-8
from vlib.url_lib import urlsCrud
import json
from django.utils.translation import ugettext as _
from django.db.models.loading import get_model
from django.apps import apps


class Grid:
    def __init__(self, model, parent_model = None, parent_pk_value = -1):
        self.model = model
        self.parent_model = parent_model
        self.parent_pk_value = parent_pk_value

    def convert_model_type_field_to_grid_type(self, model_type_field):
        if model_type_field in ("CharField", "FilePathField", "IPAddressField", "GenericIPAddressField"):
            return "text"
        if model_type_field in ("AutoField", "IntegerField", "BigIntegerField", "PositiveIntegerField",
            "PositiveSmallIntegerField", "SmallIntegerField") :
            return "number"
        if model_type_field == "ForeignKey":
            return "select"
        if model_type_field == "BooleanField":
            return "checkbox"
        if model_type_field == "DateField":
            return "date"
        if model_type_field == "DateTimeField":
            return "datetime"
        if model_type_field in ("DecimalField", "FloatField"):
            return "decimal" #sets step="any" on grid html
        if model_type_field == "EmailField":
            return "email"
        if model_type_field == "FileField":
            return "FileUpload"
        if model_type_field == "ImageField":
            return "image"
        if model_type_field == "TextField":
            return "textarea"
        if model_type_field == "TimeField":
            return "time"
        if model_type_field == "URLField" :
            return "url"

    def parse_type_field_to_text(self, field_type):        
        list_str = str(field_type).split(".")
        str_field = str(list_str[len(list_str) - 1])
        str_field = str_field[0:len(str_field) -2]
        return str_field

    def get_field_model_type_as_grid_type(self, field_type):
        return self.convert_model_type_field_to_grid_type(self.parse_type_field_to_text(field_type))
    
    def get_model_related(self, field_name, field_type):
        if self.parse_type_field_to_text(field_type) == "ForeignKey":
           return self.model._meta.get_field(field_name).rel.to
        else:
            return None   
    def get_name_column_grid(self, field_name, field_type):
        if self.parse_type_field_to_text(field_type) == "ForeignKey":
            return field_name + '_id'
        else:
            return field_name

    def get_model_attributes(self, only_this_attribute = ""):
        return {f.name : {'grid-type' : self.get_field_model_type_as_grid_type(type(f) ),
            'model' : self.get_model_related(f.name, type(f))} 
            for f in self.model._meta.fields if only_this_attribute == f.name or only_this_attribute == ""}

    def get_model_attribute(self, attribute):
        return  self.get_model_attributes(attribute)        

    def get_grid_column_model(self, field_name):
        attr = self.get_model_attribute(field_name)
        return attr[field_name]['model']

    def get_grid_column_type(self, field_name):
        attr = self.get_model_attribute(field_name)
        return attr[field_name]['grid-type']

    def get_grid_columns_config(self, field_name, read_only = True):
        if read_only:
            return {"type":"", "objects":"", "values":"", "is_link_to_form" : False } 
        attr = self.get_model_attributes(field_name)
        column_type = attr[field_name]['grid-type']
        column_model = attr[field_name]['model']

        if self.parent_model and column_model == self.parent_model:
            return {"type":"", "objects":"", "values":"", "is_link_to_form" : True }             

        
        if column_model != None:
            query = column_model.objects.all()
            str_objects, id_values = [], []
            for q in query:
                str_objects.append(str(q));
                id_values.append(str(q.id))
            return {"type":column_type, "objects":str_objects, "values":id_values, 
                "is_link_to_form" : False}
        else:
            return {"type":column_type, "objects":"", "values":"", 
                "is_link_to_form" : False}

    def get_model_field_config(self, field_name, field_config):
        return getattr(self.model._meta.get_field(field_name), field_config)            
    
    def get_data(self, fields_to_display, dict_filter):        
        if dict_filter == {}:
            if self.parent_model != None:
                for field in self.model._meta.fields:                  
                    if self.get_grid_column_model(field.name) == self.parent_model:
                        dic = {self.get_name_column_grid(field.name, type(field)) : 
                            self.parent_pk_value }
                        return self.model.objects.filter(**dic).values_list(*fields_to_display)     
            else:
                return self.model.objects.values_list(*fields_to_display)
        else:
            return self.model.objects.filter(**dict_filter).values_list(*fields_to_display)


    def get_js_grid(self, read_only = True, use_crud = False, display_fields = (),
        dict_filter = {}):        
        ''' transform the values of a model to javascript object ''' 
        # string to save columns and rows 
        columns = str()
        rows = str()
        bottom_bar = str()
        # get the fields declared on model
        fields_model = self.model._meta.fields
        fields_to_display = list(display_fields)
        if self.parent_model:
            parent_model_str = self.parent_model.__name__
        else:
            parent_model_str = str()

        url_update = str()
        url_delete = str()
        url_insert = str()

        # used to count the actual loop position's 
        loop_count = 0
        
        #used to save the register id's. Will be used on the links to delete and update
        id_registro = -1

        # this part is responsable to get the urls base of insert, delete and insert
        if use_crud:
            Urls = urlsCrud(self.model);
            url_update = Urls.BaseUrlUpdate(CountPageBack = 1)
            url_delete = Urls.BaseUrlDelete()
            url_insert = Urls.BaseUrlInsert(CountPageBack = 1)
        link_to_form = ""
        #makes the loop on fields model's, creating the columns list's. if the field is "id", dont show
        for field in fields_model:
                              
            grid_conf = self.get_grid_columns_config(field.name, read_only)
            
            if grid_conf["is_link_to_form"]:
                link_to_form = self.get_name_column_grid(field.name, type(field))

            if not display_fields :

                if self.get_model_field_config(field.name, 'editable') == False:
                    continue

                if not grid_conf["objects"]:                
                    columns += '"%s":{"name":"%s", "label":"%s", "type":"%s"},' % (field.name, 
                        self.get_name_column_grid(field.name, type(field)), field.verbose_name, grid_conf["type"])
                else:
                    columns += '"%s":{"name":"%s", "label":"%s", "type":"%s", "options":%s, "values":%s},' \
                    % (field.name, self.get_name_column_grid(field.name, type(field)), field.verbose_name, 
                        grid_conf["type"], grid_conf["objects"], grid_conf["values"] )  

                fields_to_display.append(field.name)
            else :
                temp_display = []
                for f in display_fields:
                    if f.count('__') > 0:
                        temp_display.append(f[0:f.index('__')].upper())
                    else:
                        temp_display.append(f.upper())
                    
                if field.name.upper() in temp_display:
                    columns += '"%s":{"name":"%s", "label":"%s", "type":"%s"},' % (field.name, 
                        self.get_name_column_grid(field.name, type(field)), field.verbose_name,
                        grid_conf["type"])                
                        
        if use_crud:
            columns += '"col_update":{"name":"update", "label":"%s", "type":"link"},' % ''#(_('Update'))            
            columns += '"col_delete":{"name":"delete", "label":"%s", "type":"link"},' % ''#(_('Delete'))

        #eliminates the last comma
        columns = columns[0: len(columns) - 1]
        
        #add the insert link on bar
        if use_crud:
            bottom_bar = '"link_insert":{"name":"insert", "label":"%s", "type":"link", "value" : "%s" }' % (_('Add'),
                url_insert)

        #adds the field "id" into the list. The field value will be returned but not shown.
        #it's only to create the links to update and delete
        if use_crud:
            fields_to_display.append('id')

        # get the data
        registers = self.get_data(fields_to_display = fields_to_display, dict_filter = dict_filter)

        #reset the integer variables
        columns_count = 0
        loop_count = 0 
        #variable to count the loops made in the values of the registers
        loop_count_values = 0

        #loop on registers
        for register in registers:
            list_value = ""
            id_registro = -1
            columns_count = len(register)
            loop_count_values =  0
            for jsValue in register:                
                loop_count_values += 1
                if (loop_count_values == columns_count) and (use_crud):
                    id_registro = jsValue
                else:
                    list_value += '"' + str(jsValue) + '"' + ','
            
            if use_crud:
                list_value += '"' + url_update + str(id_registro) + '"' + ','
                list_value += '"' + url_delete + str(id_registro) + '"' + ','
                list_value += '"' + url_insert + '"' + ','                

            #remove the last comma
            list_value = list_value[0: len(list_value) - 1]
            list_value = '[%s]' % (list_value)              
            rows += '"%s":{"v":%s},' % ('r' + str(loop_count), list_value)              
            loop_count += 1
        rows = rows[0 : len(rows) - 1] 
        
        return '{"columns":{%s}, "rows":{%s}, "bar":{%s}, "grid_key":"%s", "grid_mod" : "%s", '\
            '"use_crud":"%s", "read_only":"%s", "url_insert":"%s", "url_update":"%s", "url_delete":"%s", \
            "parent":"%s", "link_to_form":"%s" }' % \
            (columns, rows, bottom_bar, self.model.__module__, self.model.__name__, str(use_crud), 
            str(read_only), url_insert, url_update, url_delete, parent_model_str, link_to_form)

    @staticmethod
    def grid_script(data, model):
        script = '<div id="div_%s" class="grid table-responsive"></div>' % (model.__name__)
        script += '<script type="text/javascript">'
        script += '$(document).ready(function(){'
        script += 'Grid("div_%s",%s)' % (model.__name__, data)
        script += '});'
        script += '</script>'
        return script

    def grid_as_text(self, read_only = True, use_crud = False, display_fields = (), dict_filter = {}):   
        if read_only:
            return self.grid_script(self.get_js_grid(use_crud = use_crud, read_only = read_only, 
                display_fields = display_fields, dict_filter = dict_filter), self.model)
        else:
            if hasattr(self.model._meta, 'child_models'):
                child_models = self.model._meta.child_models
                mod = None
                script_grid = str()
                for child_model in child_models:                    
                    mod = get_model(app_label = self.model._meta.app_label, model_name = child_model)
                    GridDetalhe = Grid(mod, self.model, self.parent_pk_value)
                    script_grid += self.grid_script(data = GridDetalhe.get_js_grid(use_crud = use_crud,
                        read_only = read_only, display_fields = display_fields, dict_filter = dict_filter),
                        model = mod)
                return script_grid
            else:
                return ""
                
