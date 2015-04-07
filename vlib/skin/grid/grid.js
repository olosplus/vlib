function SetChangesLine(element){
  parent = $(element).parent().parent();  
  if(parent.attr('operation') != 'inserted'){
    parent.attr('operation','updated');
  };
};

function RemoveSelectedRows(idGrid){
  grid = $( '#' + idGrid);
  grid.find('tr[sel="true"]').remove();  
}

function selectLine(element){
  parent = $(element).parent().parent().parent();  
  
  if(element.checked === true){
    parent.attr('sel','true');
  }
  else{
    parent.attr('sel','false');
  }
  return true;    
}

function JoinToJson(key, value){
  return '"' + key.replace(" ", "") + '":"' + value + '",';
};


function GetGridChange(idGrid, operation){
  var line_separator = "<<LINE_SEPARATOR>>";
  if(operation === 'sel'){
    var list_tr = $( '#' + idGrid + ' tr[sel="' + true + '"]');
  }
  else{
    var list_tr = $( '#' + idGrid + ' tr[operation="' + operation + '"]');
  };
  var str_json = '';
  var str_row = '';
  for(tr in list_tr){
    str_row = "";
    if (list_tr.hasOwnProperty(tr)) {
      if(tr === 'context') 
        continue  
      tds = list_tr[tr].children;
      if (list_tr[tr].childElementCount  > 0) {
        str_row += '{';
      }
      for(td in tds){
        if (tds.hasOwnProperty(td)) {
          if (tds[td].childElementCount > 0){
            element = tds[td].children[0];
            if(element.nodeName === "INPUT" || element.nodeName === "TEXTAREA") {
              str_row += JoinToJson(element.name, element.value);
            };  
            if(element.nodeName === "SELECT"){
              if (element.selectedIndex > -1)
                str_row += JoinToJson(element.name, element.options[element.selectedIndex].value);
            };              
          };
        };
      };
    };  
    if (list_tr[tr].childElementCount  > 0) {
      str_row = str_row.substr(0, str_row.length - 1);
      str_row += '}' + line_separator + " ";
      if (str_row != '}' + line_separator + " "){
        str_json += str_row;
      }
    };
  };
  str_json = str_json.substr(0, str_json.length - 1);
  
//  var grid = $("#" + idGrid);
  return str_json;  
};
function getAttrGrid(idGrid, attr){
  var grid = $("#" + idGrid);
  return grid.attr(attr)
}
function ParseGridToJson(idGrid){
  return {rows_inserted : GetGridChange(idGrid, "inserted"), rows_updated : GetGridChange(idGrid, "updated"),    
    model : getAttrGrid(idGrid,'mod'), module : getAttrGrid(idGrid,'module'), 
    link_to_form : getAttrGrid(idGrid, 'link_to_form') };
}

function ParseGridToJsonDelete(idGrid){
  return {rows_deleted : GetGridChange(idGrid, "sel"),
    model : getAttrGrid(idGrid,'mod'), module : getAttrGrid(idGrid,'module') };
}

function InsertEmptyRow(columns, idGrid, link_to_form){
    var html_input = "<input type='{{TYPE}}' value='{{VALOR}}' {{DISABLE}} {{STEP}} "+
      "class = 'gridtag' name = {{NAME}} onchange='SetChangesLine(this)'></input>";
    var type_input = "";

      html = "<tr operation='inserted' sel='true'>";
      html += "<td> <center><input type='checkbox' checked onchange='selectLine(this)'></input> </td></center>";
      for (column in columns) {
        if (columns.hasOwnProperty(column)) {
          if(columns[column].type === 'link'){
            continue;
          };
          if ((columns[column].name === "id")||(columns[column].name === link_to_form)){
            html += "<td class='notvis'>";
          }
          else{
            html += "<td>"; 
          }
          //for inputs
          if( (columns[column].type != 'select')  && (columns[column].type != 'link' ) && 
              (columns[column].type != 'textarea') ){
            html += html_input.replace('{{TYPE}}', columns[column].type);
            html = html.replace('{{VALOR}}', "");
            html = html.replace('{{DISABLE}}', '');
            html = html.replace('{{NAME}}', columns[column].name);            
            if (columns[column].type === 'decimal'){
              html = html.replace("{{STEP}}", "step='any'");
            }
            else{
              html = html.replace("{{STEP}}", "");
            };
          };
          if (columns[column].type === 'textarea'){
            html += "<textarea class = 'gridtag' name='" + columns[column].name + "' onchange='SetChangesLine(this)'>"+
              "</textarea>";
          };
          if (columns[column].type == 'select') {
            if (columns[column].options != 'undefined') {
              var options = columns[column].options;
              var values = columns[column].values;
              html += "<select class = 'gridtag' name='"+ columns[column].name + "' onclick='SetChangesLine(this)'>";
              for (option in options) {
                if (options.hasOwnProperty(option)) {
                  html += "<option value='" + values[option] + "'>";
                  html += options[option] + "</option>";
                };
              };
              html += "</select>";
            };
          };  
        };    
        html += "</td>";
      };
    html += "</tr>";
    body = $("#" + idGrid + "> tbody");
    $("#" + idGrid + "> tbody").append(html);
};

function InsertLineWithValue(row, columns, readonly, link_to_form){
  var html_input = "<input type='{{TYPE}}' value='{{VALOR}}' {{STEP}} class = 'gridtag' name = "+
    "{{NAME}}  onchange='SetChangesLine(this)'>"+
      "</input>";
  var type_input = "";
  var class_links = "";
  var events = "";
  var index = 0;

      html = "<tr>";
      if(readonly === "False"){
        html += "<td> <center><input type='checkbox' onchange='selectLine(this)'> "+
          "</input> </td></center>";
      };
      for (column in columns) {
        if (columns.hasOwnProperty(column)) {
          if ((columns[column].type === 'link')  && (readonly === "False")) {
            continue;
          };
          if ((columns[column].name === "id") || (columns[column].name === link_to_form)) {
            html += "<td class = 'notvis'>";
          }
          else{
            html += "<td>"
          }  
          //for inputs
          if( (columns[column].type != 'select')  && (columns[column].type != 'link' ) && 
              (columns[column].type != 'textarea') && (columns[column].type != "") ){
            html += html_input.replace('{{TYPE}}', columns[column].type);
            html = html.replace('{{VALOR}}', row.v[index]);
            html = html.replace('{{NAME}}', columns[column].name);            
            if (columns[column].type === 'decimal'){
              html = html.replace("{{STEP}}", "step='any'");
            }
            else{
              html = html.replace("{{STEP}}", "");
            };
          };
          if (columns[column].type === 'textarea'){
            html += "<textarea class = 'gridtag' name='" + columns[column].name + "' onchange='SetChangesLine(this)'>" +
              row.v[index] + "</textarea>"
          };
          if ((columns[column].type === 'link') && (readonly === "True")) {
              if(columns[column].name === "update"){
                 class_links = "fa fa-pencil";
              }
              else{
                if(columns[column].name = "delete"){
                  class_links = "fa fa-trash-o";
                  events = 'return confirm("Deseja realmente deletar este registro ?")';
                };
              };
              html += "<center><a  href = '" + row.v[index] + "' class='"+ class_links +"' title= '"+
                columns[column].label  +"' onclick='"+ events +"'>" +
                "</a></center>";
          };
          if (columns[column].type == 'select') {
            if (columns[column].options != 'undefined') {
              var options = columns[column].options;
              var values = columns[column].values;
              html += "<select class = 'gridtag' name=' " + columns[column].name + "' "+
                " onclick='SetChangesLine(this)' onkeydown='SetChangesLine(this)'>";
              for (option in options) {
                if (options.hasOwnProperty(option)) {
                  html += "<option value='" + values[option] + "'";
                  if (row.v[index] === values[option]) {
                    html += "selected>";
                  } else {
                    html += ">";
                  };
                  html += options[option] + "</option>";
                };
              };
              html += "</select>";
            };
          };  
          if(columns[column].type === ""){
            html += row.v[index];
          };
        };    
        html += "</td>";
        index += 1;
      };
    
    html += "</tr>";
    return html
};

function Grid(DivGridId, Data) {

  var columns = Data.columns;
  var rows = Data.rows;
  var bar = Data.bar;
  var module =  Data.grid_key;
//  var array_module = module.split(".");
  var grid_id = Data.grid_mod;//array_module[array_module.length - 2];
  var model = Data.grid_mod;
  var use_crud = Data.use_crud;
  var readonly = Data.read_only;
  var url_insert = Data.url_insert;
  var url_update = Data.url_update;
  var url_delete = Data.url_delete;
  var parent = Data.parent;
  var link_to_form = Data.link_to_form;
  var html = "<div class='grid'><table id='" + grid_id + "' parent='"+ parent + "'" + 
    "link_to_form='" + link_to_form + "'" +
    " class='tablegrid table table-bordered table-hover table-striped' module='"+ module + "' " +
    "mod='" + model + "'><thead class = 'header'> <tr>";
  if(readonly === "False"){
    html += "<th><center>*</center></th>";
  };
  for (column in columns) {
    if (columns.hasOwnProperty(column)) {
      if ((columns[column].type === 'link')  && (readonly === "False")) {
        continue;
      };
      if ((columns[column].name === "id")||(columns[column].name === link_to_form)){
        html += "<th class='notvis'>" + columns[column].label + "</th>";
      }
      else{
        html += "<th>" + columns[column].label + "</th>";
      }
    };
  };
  html += "</tr></thead>";
  html += "<tbody>"
  for (row in rows) {
    if (rows.hasOwnProperty(row)) {
      html += InsertLineWithValue(rows[row], columns, readonly, link_to_form)      
    };
  };

  html += "</tbody>";
  html += "</table>";

  for (item_bar in bar) {
    if (bar.hasOwnProperty(item_bar)) {
      if ((bar[item_bar].type === 'link') && (readonly === "True")){
        html += "<a class = 'fa fa-file-o' href = '" + bar[item_bar].value + "' title='"+ bar[item_bar].label +"'>" +
          "</a>";
      };
    };
  };
  if (readonly === "False"){
    html += "  <a href='#' class='fa fa-file-o' title='Adicionar'"+
      "onclick='InsertEmptyRow("+ JSON.stringify(columns) + ",\""+ grid_id  +"\", \"" + link_to_form + "\" )'>"+
      "</a> | ";

    html += "  <a href='#' id='linkcancel' class='glyphicon glyphicon-floppy-remove' "+
      "onclick='RemoveSelectedRows(\""+ grid_id  +"\" )' title='Cancelar'>"+
      "</a> | ";

    html += "  <a href='#' onclick='doDeleteGrid(\"" + grid_id + "\")' class = 'fa fa-trash-o' "+
      "title='Deletar selecionados'></a> | ";
   
    html += "  <a href='#' onclick='doPostGrid(\"" + grid_id + "\")' class='glyphicon glyphicon-floppy-disk' "+
      " title='Salvar'></a>";
  };

  html += "</div>"
  $("#" + DivGridId).html(html);
  
};


function doPostGrid(idGrid){
  var parent = $('#' + idGrid).attr('parent');
  var sequence = "";
  if ((parent != "") && (parent != undefined)){
    sequence = $('#' + parent).attr('sequence');
    var link_to_form = $('#' + idGrid).attr('link_to_form');
    if ((sequence != "") && (sequence != undefined)){
      $("#" + idGrid + " input[name= '" + link_to_form + "'").each(function(){
        $(this).attr("value", sequence);
      });                      
    }else{
      sequence = "";
    };
  };
  if(parent != ""){
    var send_to = $('#ownurl').val();
    var redirect_to = $('#listurl').val();
    doPostForm(send_to, parent, "", false, "");    
  }else{
    var jsgrid = ParseGridToJson(idGrid);
    $.ajax({
      url: '/savegrid',    
      type: 'get', //this is the default though, you don't actually need to always mention it
      data: jsgrid ,
      success: function(data) {
        var parser = new DOMParser()
        var doc_received = parser.parseFromString(data, "text/html");
        var erros = doc_received.getElementById('grid_erros');
        if(erros != null){
          alert(erros.value);
        }else{
          alert('Dados salvos com sucesso!');
        }
      },
      failure: function(data) { 
        alert('Got an error dude');
      }
    });     
  };
};

function doDeleteGrid(idGrid){
  var parent = $('#' + idGrid).attr('parent');
  if (parent === ""){
    jsgrid = ParseGridToJsonDelete(idGrid);
    $.ajax({
      url: '/deletegrid',    
      type: 'get', //this is the default though, you don't actually need to always mention it
      data: jsgrid ,
      success: function(data) {
          alert(data);
          RemoveSelectedRows(idGrid);
      },
      failure: function(data) { 
          alert('Got an error dude');
      }
    });   
  }else{
    var send_to = $('#ownurl').val();
    var redirect_to = $('#listurl').val();
    doPostForm(send_to, parent, "", true, idGrid);
    RemoveSelectedRows(idGrid);
  };  
}

// using jQuery
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
      }
    }
  }
  return cookieValue;
}

/*pqp não entendi nada dessa porra - usado para o csrf_token do django*/
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function doPostForm(send_to, form_id, url_redirect, is_delete, id_grid_delete){
  var form = $('#' + form_id);
  var url = send_to;
  var csrftoken = getCookie('csrftoken');
  var jsgrid = "";
  if(is_delete === false){ 
    $('table[parent="' + form_id +'"]').each(function(){
       jsgrid += JSON.stringify(ParseGridToJson($(this).attr('id'))) + "[[<<ROW_SEPARATOR>>]]";
    });
  }else{
    jsgrid += JSON.stringify(ParseGridToJsonDelete(id_grid_delete)) + "[[<<ROW_SEPARATOR>>]]";
  };

  form.append("<input type='hidden' name='child_models' value='"+ jsgrid +"'></input>");

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
  
  $.ajax({
    url: url,    
    type: 'post', //this is the default though, you don't actually need to always mention it
    data: form.serialize(),
    success: function(data) {
  
      var parser = new DOMParser()
      var doc_received = parser.parseFromString(data, "text/html");
      var frm_received = doc_received.getElementById(form_id); 
      if (frm_received === null){
        var erros = doc_received.getElementById("grid_erros");
        if (erros != null){
          alert(erros.value);        
        }else{
          if (url_redirect != ""){
            window.location.href = url_redirect;
          }else{
            alert('Dados atualizados com sucesso!');
          };
        };
      }else{      
        var frm = document.getElementById(form_id);
        if (frm_received.innerHTML === ""){
          if (url_redirect != ""){
            window.location.href = url_redirect;
          }else{
            alert('Dados atualizados com sucesso!');
          }
        }else{
          frm.innerHTML = frm_received.innerHTML;
        }    
      }
    },
    error: function(data) { 
        alert(data.responseText);
    }
  });
  return false;
};



