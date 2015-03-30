function SetChangesLine(element){
  parent = $(element).parent().parent();  
  if(parent.attr('operation') != 'inserted'){
    parent.attr('operation','updated');
  };
};

function JoinToJson(key, value){
  return '"' + key.replace(" ", "") + '":"' + value + '",';
};

function GetGridChange(idGrid, operation){
  var list_tr = $('tr[operation*="' + operation + '"]')
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
              str_row += JoinToJson(element.name, element.options[element.selectedIndex].value);
            };              
          };
        };
      };
    };  
    if (list_tr[tr].childElementCount  > 0) {
      str_row = str_row.substr(0, str_row.length - 1);
      str_row += '}|';
      if (str_row != '}|'){
        str_json += str_row;
      }
    };
  };
  str_json = str_json.substr(0, str_json.length - 1);
  
  var grid = $("#" + idGrid);
  return str_json;  
};
function getAttrGrid(idGrid, attr){
  var grid = $("#" + idGrid);
  return grid.attr(attr)
}
function ParseGridToJson(idGrid){
  return {rows_inserted : GetGridChange(idGrid, "inserted"), rows_updated : GetGridChange(idGrid, "updated"), 
    model : getAttrGrid(idGrid,'mod'), module : getAttrGrid(idGrid,'module') };
}

function InserirLinha(columns, idGrid){
    var html_input = "<input type='{{TYPE}}' value='{{VALOR}}' {{DISABLE}} {{STEP}} "+
      "class = 'gridtag' name = {{NAME}} onchange='SetChangesLine(this)'></input>";
    var type_input = "";

      html = "<tr operation='inserted'>";
      html += "<td></td>";
      for (column in columns) {
        if (columns.hasOwnProperty(column)) {
          html += "<td>";
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
            html += "<textarea class = 'gridtag' name='" + columns[column].name + "'></textarea>";
          };
          if (columns[column].type == 'select') {
            if (columns[column].options != 'undefined') {
              var options = columns[column].options;
              var values = columns[column].values;
              html += "<select class = 'gridtag' name='"+ columns[column].name + "' >";
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

function Grid(GridId, Data, editable) {

  var disable = "";

  if (editable == false) {
    disable = "readonly";
  };
  var columns = Data.columns;
  var rows = Data.rows;
  var bar = Data.bar;
  var module =  Data.grid_key;
  var array_module = module.split(".");
  var grid_id = array_module[array_module.length - 2];
  var model = Data.grid_mod;
  var html_input = "<input type='{{TYPE}}' value='{{VALOR}}' {{DISABLE}} {{STEP}} class = 'gridtag' name = "+
    "{{NAME}}  onchange='SetChangesLine(this)'>"+
      "</input>";
  var type_input = "";

  var html = "<div class='grid'><table id='" + grid_id + "' class='tablegrid' module='"+ module + "' " +
    "mod='" + model + "'><thead class = 'header'> <tr>";
  html += "<th>*</th>";
  for (column in columns) {
    if (columns.hasOwnProperty(column)) {
      html += "<th>" + columns[column].label + "</th>";
    };
  };
  html += "</tr></thead>";
  html += "<tbody>"
  for (row in rows) {
    var index = 0;
    if (rows.hasOwnProperty(row)) {
      html += "<tr>";
      html += "<td class ='" + disable + "'></td>";
      for (column in columns) {
        if (columns.hasOwnProperty(column)) {
          html += "<td>";
          //for inputs
          if( (columns[column].type != 'select')  && (columns[column].type != 'link' ) && 
              (columns[column].type != 'textarea') ){
            html += html_input.replace('{{TYPE}}', columns[column].type);
            html = html.replace('{{VALOR}}', rows[row].v[index]);
            html = html.replace('{{DISABLE}}', disable);
            html = html.replace('{{NAME}}', columns[column].name);            
            if (columns[column].type === 'decimal'){
              html = html.replace("{{STEP}}", "step='any'");
            }
            else{
              html = html.replace("{{STEP}}", "");
            };
          };
          if (columns[column].type === 'textarea'){
            html += "<textarea class = 'gridtag' name='" + columns[column].name + "'>" +
              rows[row].v[index] + "</textarea>"
          };
          if (columns[column].type === 'link') {
            if (columns[column].event != "undefined") {
              html += "<a  href = '" + rows[row].v[index] + "' " + columns[column].event + " " + disable + ">" +
                columns[column].label + "</a>";
            } else {
              html += "<a  href = '" + rows[row].v[index] + "' " + disable + ">" + columns[column].label + "</a>";
            };
          };
          if (columns[column].type == 'select') {
            if (columns[column].options != 'undefined') {
              var options = columns[column].options;
              var values = columns[column].values;
              html += "<select class = 'gridtag' name=' " + columns[column].name + "'>";
              for (option in options) {
                if (options.hasOwnProperty(option)) {
                  html += "<option value='" + values[option] + "'";
                  if (rows[row].v[index] === values[option]) {
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
        };    
        html += "</td>";
        index += 1;
      };
    };
    html += "</tr>"
  };

  html += "</tbody>";
  html += "</table>";

  for (item_bar in bar) {
    if (bar.hasOwnProperty(item_bar)) {
      if (bar[item_bar].type === 'link') {
        html += "<a  href = '" + bar[item_bar].value + "'>" + bar[item_bar].label + "</a>";
      };
    };
  };
  html += "  <a href='#' id='gridInsert' onclick='InserirLinha("+ JSON.stringify(columns) + ",\""+ grid_id  +"\" )'>"+
    "Inserir Linha</a>";

  html += "  <a href='#' onclick='doPostGrid(\"" + grid_id + "\")'>"+
    "Salvar</a>";

  html += "</div>"
  $("#" + GridId).html(html);
  
};


function doPostGrid(idGrid){
  jsgrid = ParseGridToJson(idGrid);
  $.ajax({
    url: '/savegrid',    
    type: 'get', //this is the default though, you don't actually need to always mention it
    data: jsgrid ,
//    contentType: 'application/json; charset=utf-8', 
    success: function(data) {
        alert(data);
    },
    failure: function(data) { 
        alert('Got an error dude');
    }
  });   
}

