const my_ip = "http://127.0.0.1:5000/"

// Function to pan and zoom the svg
window.addEventListener('load', () => {
  $("select").select2();
  initModel()
});

window.sessionStorage.setItem('server_url',JSON.stringify({"server_ip":my_ip}))
window.setInterval(handleUpdate, 4000, false)
window.sessionStorage.setItem("last_update", new Date(0).toISOString())
parser = new DOMParser();

// Select tab
let tablinks = document.querySelectorAll(".tablinks");
tablinks.forEach((tablink) => {
  tablink.addEventListener("click", function openTab(evt) {
    let i, tabcontent;

    // remove the tab content
    tabcontent = document.querySelectorAll(".tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }

    // remove the active class from the tab link
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace("active", "");
    }

    // add active class to clicked tab and show the corresponding content
    document.getElementById(
      evt.target.getAttribute("data-tabId")
    ).style.display = "block";
    evt.target.classList.add("active");
  });
});

// Listen to selected MSI button on MSI info tab
document.addEventListener('click', (event)=> {
  if (event.target.classList.contains("MSI_link")) {
    $('#searchbar_MSI').val(event.target.getAttribute("data-value")); // Select the option with a value of '1'
    $('#searchbar_MSI').trigger('change'); // Notify any JS components that the value changed
  }
})

// Listen to selected MSI on MSI info tab and fill table with correct data
$("#searchbar_MSI").on("change", showMsiData);

$("#req_list_searchbar").on("select2:select", function (event) {
  let data = window.sessionStorage.getItem("request_list")
  data = JSON.parse(data)
  
  let myKey = event.params.data.id
  let tabData = Object.entries(data[myKey])
  
  createRequestListTable(tabData,myKey)
});

document.getElementById("Req_list_button").addEventListener('click', createRequestList);
document.getElementById("Req_add_button").addEventListener('click', (event) => {
  let data = JSON.parse(window.sessionStorage.getItem("MSI_data_parsed"))
  let unp_data = JSON.parse(window.sessionStorage.getItem("MSI_data"))
  createRequestAdditionList(data,unp_data)

});
// listen to request removal
document.getElementById("button_remove_request").addEventListener('click', handleRemoveEvent)

///////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////    Function definitions      /////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////

// Initialize model and client.
async function initModel() {
    let jsondata
    const datasetId = new URL(window.location.href).searchParams.get("datasetId")
    if (datasetId == null) {
        //manual reloading
        console.log("hi")
        await handleUpdate(true)
    } else {
        jsondata = window.sessionStorage.getItem("MSI_data_parsed")
        if (jsondata == null) {
            await getDataset("initModel", {"datasetId":datasetId})
        }
    }
    initSvg()

    jsondata = window.sessionStorage.getItem("MSI_data_parsed")
    createTabsWithTable(JSON.parse(jsondata),"searchbar_MSI")
    createRequestList()
}

// Send a new measure request.
async function handleSendRequest(){
  request = requestToJSON()

  if (request) {
    clearRequestAdditionList()

    await getDataset("runNewRequest", request)
    updateSvg()
    createRequestList()
  }
}

// Remove an existing measure request.
async function handleRemoveEvent(ev) {
  request = {
    "type" : "remove",
    "name": ev.target.value
  }

  await getDataset("removeRequest", request)
  updateSvg()
  createRequestList()
}

// Check the server for updates.
async function handleUpdate(first_creation){
    request = {
      "type":"update",
      "time": window.sessionStorage.getItem("last_update")
    }

    if (await getDataset("getChanges", request)) {
        if (document.getElementById('Req_list').getAttribute("style") == "display: block;") {
            createRequestList()
        }
        if (!first_creation) {
            updateSvg()
        }
    }
}

// Send a request to 'address' with data 'request', and store the received data. Returns true if data changed.
async function getDataset(address, request) {
    // Some time passes between sending and updating, this prevents missing updates in that timespan.
    newTime = new Date().toISOString()
    server_ip = JSON.parse(window.sessionStorage.getItem("server_url"))
    response = await fetch(server_ip.server_ip+address, {
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
        body: JSON.stringify(request)
    })
    dataset = await response.json()
    if (dataset.update) {
        window.sessionStorage.setItem("MSI_data",JSON.stringify(dataset.data))
        window.sessionStorage.setItem("MSI_data_parsed",JSON.stringify(parseData(dataset.data)))
        window.sessionStorage.setItem("SVG_data",JSON.stringify(dataset.svg))
        window.sessionStorage.setItem("request_list",JSON.stringify(dataset.constraints_list))
        window.sessionStorage.setItem("last_update", newTime)
        return true
    }
    return false
}

// Create controllable SVG image.
function initSvg() {
    let svgdata = window.sessionStorage.getItem("SVG_data")
    document.getElementById('svg_div').innerHTML = JSON.parse(svgdata)
    initPanZoom('#svg5')
    updateSvgNames()
}

// Create a list of existing requests.
function createRequestList() {
  let data = window.sessionStorage.getItem("request_list")
  if (data != {}) {
    data = JSON.parse(data)
  }

  const list_of_keys = Object.keys(data);
  document.getElementById("req_list_searchbar").innerHTML = list_of_keys.map(
    (name) => `<option value="${name}">${name}</option>`
  );

  if (list_of_keys.length > 0) {
    let myKey = list_of_keys[0]
    let tabData = Object.entries(data[myKey])
    createRequestListTable(tabData,myKey)
  } else {
    document.getElementById("req_constr_table").innerHTML = ""
    document.getElementById("button_remove_request").setAttribute("disabled","")
  }
}

// Create a table notation of a request.
function createRequestListTable(data,myKey) {
  let deleteButton = document.getElementById("button_remove_request")
  let allowDelete = true

  let options_list = data.map(entry => {
      if (entry[1].includes("v_vrij")) {
        return {"V-VRIJ": entry[1].split('[')[1].split(',')[0]}
      }
      if (entry[1].includes("dyn_max_speed")) {
        return {"DYN_V" : entry[1].split('[')[1].split(',')[0]}
      }
      if (entry[1].includes("RHL")) {
        return {"RHL" : entry[1].split('[')[1].split(']')[0]}
      }
      if (entry[1].includes("]_aid") && entry[1].includes('trafficstream')) {
        return {"AID" : entry[1].split('[')[1].split(']')[0].replace(',',', TS ')}
      }
    }).filter(x => x !== undefined);

  options_obj = {}
  for (let i = 0; i<options_list.length; i++) {
    if (Object.keys(options_obj).includes(Object.keys(options_list[i])[0])) {
      options_obj[Object.keys(options_list[i])[0]].push(Object.values(options_list[i])[0])
    } else {
      options_obj[Object.keys(options_list[i])[0]] = Object.values(options_list[i])
      if (Object.keys(options_list[i])[0].includes('RHL')) {
        allowDelete = false
      }
    }
  }

  document.getElementById("req_constr_table").innerHTML = `
<table>
  <thead>
    <td>MSI</td>
    <td>Legend</td>
  </thead>
  <tbody>
    ${data.map(entry => {
      let split_data = entry[1].split('[')
      if (split_data[1].slice(-1) == ']') {
        let legend = legendLetterToWord(split_data[0].slice(-1))
        let MSI = parseRSUString("["+split_data[1])
        return `<tr><td>${MSI}</td><td>${legend}</td></tr>`
      }

      }).join("")
    }
  </tbody>
</table>

<table>
  <thead>
    <td>Options</td>
    <td>Location</td>
  </thead>
  <tbody>
    ${Object.entries(options_obj).map(entry => { {
        return `<tr><td rowspan="${entry[1].length+1}">${entry[0]}</td><td>  </td></tr>
        ${entry[1].map(value => {return `<tr><td>${parseRSUString(value)}</td></tr>`} ).join("")}`
      }
      }).join("")
    }
  </tbody>
</table>`

  if (allowDelete) {
    let buttonValue = myKey
    deleteButton.setAttribute("value",buttonValue)
    deleteButton.removeAttribute("disabled")
  } else {
    deleteButton.setAttribute("disabled","")
  }
}

// fill a tab with a table
function createTabsWithTable(data,element_id) {
  const list_of_keys = Object.keys(data);
    document.getElementById(element_id).innerHTML = list_of_keys.map(
      (name) => `<option value="${name}">${name}</option>`
    );
    let tabData = Object.entries(data[list_of_keys[0]]).filter(
      ([_, value]) => value != null
    );
    createTableFromJSON(tabData);
}

// update the shown MSI info
function showMsiData() {
  let jsondata = window.sessionStorage.getItem("MSI_data_parsed")
  jsondata = JSON.parse(jsondata)
  let myKey = document.getElementById("searchbar_MSI").value;
  let tabData = Object.entries(jsondata[myKey]).filter(
    ([_, value]) => value != null
  );

  createTableFromJSON(tabData);
}

// create svg and update event handlers
function updateSvg() {
    let svgdata = window.sessionStorage.getItem("SVG_data")
    doc = parser.parseFromString(JSON.parse(svgdata), "image/svg+xml");
    newSvg = ""
    for (group of doc.getElementById("svg5").children) {
        if (group.nodeName != "g") { continue }
        newSvg += group.outerHTML
    }
    svgOuter = document.querySelectorAll('[id^="viewport-"]')[0]
    svgOuter.innerHTML = newSvg
    updateSvgNames()
    showMsiData()
}

// reset view button
function handleSVGReset (ev) {
  panZoom.resetZoom()
  panZoom.resetPan()
  document.getElementById("show-names").checked = false
  updateSvgNames()
}

// Update svg to show or hide labels.
function updateSvgNames() {
  if (document.getElementById("show-names").checked) {
    document.getElementById('nametags_MSI').setAttribute('visibility','visible');
  } else {
    document.getElementById('nametags_MSI').setAttribute('visibility','collapse');
  }
}

// initiate panZoom module for the svg
function initPanZoom(svgHandle) {
  panZoom = svgPanZoom(svgHandle, {
    zoomEnabled: true,
    panEnabled: true,
    controlIconsEnabled: false,
    zoomScaleSensitivity: 0.5,
    dblClickZoomEnabled: false,
  });

  document.getElementById("reset").addEventListener("click", handleSVGReset)
  document.getElementById("zoom-out").addEventListener("click", function(){panZoom.zoomOut()})
  document.getElementById("zoom-in").addEventListener("click", function(){panZoom.zoomIn()})
  document.getElementById("show-names").addEventListener("change", updateSvgNames)
}

// fill table with MSI data
function createTableFromJSON(tabData) {
  document.getElementById("MSI_info_table").innerHTML = `<table>
	<thead>
	  <td>Key</td>
	  <td>Value</td>
	</thead>
	<tbody>
	  ${tabData
      .map(([key, value]) => {
        if ([
          "Downstream",
          "Downstream secondary",
          "Downstream taper",
          "Downstream broadening",
          "Downstream narrowing",
          "Upstream",
          "Upstream secondary",
          "Upstream taper",
          "Upstream broadening",
          "Upstream narrowing",
          'Left',
          'Right',
          'Traffic stream right',
          'Traffic stream left',
          'Carriageway left',
          'Carriageway right'].some(a => a === key)) {
          return `<tr><td>${key}</td><td><button type="button" class="MSI_link" data-value="${value}">${value}</button></td></tr>`
        }
        if (['Traffic stream',
          'Carriageway',
          'Row'].some(a => a === key)) {
          return `<tr><td>${key}</td><td>${value.map((val) => `<button type="button" class="MSI_link" data-value="${val}">${val}</button>`)}</td></tr>`
        }
        else {
          return `<tr><td>${key}</td><td>${value}</td></tr>`
        }
      })
      .join("")}
	</tbody>
</table>`;
}

function parseData(data) {
  let parsedData = {}
  const list_of_keys = Object.keys(data);

  list_of_keys.map((i) => {parsedData[parseRSU(i)] = {
      "Legend shown": parseLegend(data[i].State),
      "Active constraints": ["None"],
      "Downstream": parseRSU(data[i].d),
      "Downstream secondary": parseRSU(data[i].ds),
      "Downstream taper": parseRSU(data[i].dt),
      "Downstream broadening": parseRSU(data[i].db),
      "Downstream narrowing": parseRSU(data[i].dn),
      "Upstream": parseRSU(data[i].u),
      "Upstream secondary": parseRSU(data[i].us),
      "Upstream taper": parseRSU(data[i].ut),
      "Upstream broadening": parseRSU(data[i].ub),
      "Upstream narrowing": parseRSU(data[i].un),
      "Right": parseRSU(data[i].r),
      "Left": parseRSU(data[i].l),
      "STAT-V": data[i]['STAT-V'],
      "DYN-V": data[i]['DYN-V'],
      "Continue cross": data[i]['C-X'],
      "Continue speed": data[i]['C-V'],
      "Traffic stream": parseRSU(data[i].T),
      "Traffic stream right": parseRSU(data[i].T_right),
      "Traffic stream left": parseRSU(data[i].T_left),
      "DIF-V from right": data[i]['DIF-V_right'],
      "DIF-V from left": data[i]['DIF-V_left'],
      "Carriageway": parseRSU(data[i].W),
      "Carriageway right": parseRSU(data[i].W_right),
      "Carriageway left": parseRSU(data[i].W_left),
      "Row": parseRSU(data[i].row),
      "Lanes in row": data[i].N_row,
      "Lanes in traffic stream": data[i].N_T,
      "Lanes in carriageway": data[i].N_W
    }
  })
  return parsedData
}

function parseRSUString(data) {
  data = data.replace(/[\[\]]+/g,'')
  new_string = ''
  split_data = data.split('_')
  for (let i = 0; i < split_data.length; i++) {
    if (split_data[i].includes('RSU')){
      continue
    }
    new_string = new_string + split_data[i] + ' '
  }

  return new_string
}

function parseRSU(data) {
  if (data == null) {
    return null
  }

  if (typeof data == 'string') {
    return parseRSUString(data)
  }

  if (typeof data == 'object') {
    let new_object = []
    let new_string = null
    for (let i=0; i < data.length; i++) {
      new_string = parseRSUString(data[i])
      new_object.push(new_string)
    }
    return new_object
  }
}

function parseLegend(data) {
  if (data.length == 1) {
    return legendLetterToWord(data[0])
  }

  legend_string = []
  for (let i = 0; i < data.length; i++) {
    legend_string.push(legendLetterToWord(data[i]))
  }
  return legend_string
}

function legendLetterToWord(data){
  if (data == 'Blank') {return "Blank"}
  if (data == 'x') {return "Cross"}
  if (data == 'r') {return "Right arrow"}
  if (data == 'l') {return "Left arrow"}
  if (data == 'o') {return "Overruling blank"}
  if (data == 'e') {return "Speed 50"}
  if (data == 'g') {return "Speed 70"}
  if (data == 'h') {return "Speed 80"}
  if (data == 'i') {return "Speed 90"}
  if (data == 'j') {return "Speed 100"}
  if (data == 'y') {return "Green arrow"}
  if (data == 'z') {return "End of restrictions"}
  if (data == 'a') {return "Flashers"}
  if (data == 'b') {return "Red ring"} 
}

function legendWordToLetter(data){
  if (data == "cross")               {return "x"}
  if (data == "right arrow")         {return "r"}
  if (data == "left arrow")          {return "l"}
  if (data == "overruling blank")    {return "o"}
  if (data == "speed 50")            {return "e"}
  if (data == "speed 70")            {return "g"}
  if (data == "speed 80")            {return "h"}
  if (data == "speed 90")            {return "i"}
  if (data == "speed 100")           {return "j"}
  if (data == "green arrow")         {return "y"}
  if (data == "end of restrictions") {return "z"}
  if (data == "flashers")            {return "a"}
  if (data == "red ring")            {return "b"}
}

function clearRequestAdditionList(){
  $('.list_input').val("")
  $('.list_input').keyup();
  $('#request_name_user_input').val("")
  $('.req_ul').html("")
  $( "#V-Vrij_check" ).prop( "checked", false )
  $("#fileupload_1").val(null);

  $("#RHL_selector").val("open")
  $('#RHL_selector').trigger('change')

  $("#DYNV_selector").val("100")
  $('#DYNV_selector').trigger('change')

  $("#AID_selector").val("50")
  $('#AID_selector').trigger('change')
}

function createRequestAdditionList(data,unparsed_data) {
  let list_of_keys = Object.keys(data);
  let list_of_rhl = new Set()
  let list_of_rsu = new Set()
  let list_of_ts = new Set()

  document.getElementById("MSI_list_UL").innerHTML = list_of_keys.map(
    (name) => `<li><button type="button" onclick="handleReqAddMSI()" class="req_add_button" name="${name}">${name}</button></li>`
  ).join("");

  Object.values(unparsed_data).forEach(value => { 
    if (value["RHL"] != null) {
      list_of_rhl.add(parseRSUString(value["RHL"]))
    }
  })
  
  $("#RHL_list_UL").html([...list_of_rhl].map(
    (name) => `<li><button type="button" onclick="handleReqAddRHL()" class="req_add_button" name="${name}">${name}</button></li>`
  ).join(""));

  Object.values(unparsed_data).forEach(value => { 
    if (value["RSU"] != null) {
      list_of_rsu.add(parseRSUString(value["RSU"]))
    }
  })

  $("#DYNV_list_UL").html([...list_of_rsu].map(
    (name) => `<li><button type="button" onclick="handleReqAddDYNV()" class="req_add_button" name="${name}">${name}</button></li>`
  ).join(""));

  Object.values(unparsed_data).forEach(value => {
    list_of_ts.add(parseRSUString(value["RSU"]) +  "TS " + value["T_num"])
  })

  $("#AID_list_UL").html([...list_of_ts].map(
    (name) => `<li><button type="button" onclick="handleReqAddAID()" class="req_add_button" name="${name}">${name}</button></li>`
  ).join(""));
}

function handleReqAddMSI() {
  let name = event.target.innerText
  let found = false
  $("#MSI_list_req_UL li").each((id, elem) => {
    if (elem.getAttribute("name") == name) {
      found = true;
    }
  });

  if (found == false) {
    document.getElementById("MSI_list_req_UL").innerHTML += `<li name="${name}">${name} 
  <select name="legend" id="legend_selector_${name}">
    <option value="cross">cross</option>
    <option value="right arrow">right arrow</option>
    <option value="left arrow">left arrow</option>
    <option value="overruling blank">overruling blank</option>
    <option value="speed 50">speed 50</option>
    <option value="speed 70">speed 70</option>
    <option value="speed 80">speed 80</option>
    <option value="speed 90">speed 90</option>
    <option value="speed 100">speed 100</option>
  </select><button type="button" onclick="handleReqRemButton()" value="${name}">x</button></li>`
  }
}

function handleReqAddRHL() {
  let name = event.target.innerText
  let found = false
  $("#RHL_list_req_UL li").each((id, elem) => {
    if (elem.getAttribute("name") == name) {
      found = true;
    }
  });

  if (found == false) {
    document.getElementById("RHL_list_req_UL").innerHTML += `<li name="${name}">${name} 
  <button type="button" onclick="handleReqRemButton()" value="${name}">x</button></li>`
  }
}

function handleReqAddDYNV() {
  let name = event.target.innerText
  let found = false
  $("#DYNV_list_req_UL li").each((id, elem) => {
    if (elem.getAttribute("name") == name) {
      found = true;
    }
  });

  if (found == false) {
    document.getElementById("DYNV_list_req_UL").innerHTML += `<li name="${name}">${name} 
    <button type="button" onclick="handleReqRemButton()" value="${name}">x</button></li>`
  }
}

function handleReqAddAID() {
  let name = event.target.innerText
  let found = false
  $("#AID_list_req_UL li").each((id, elem) => {
    if (elem.getAttribute("name") == name) {
      found = true;
    }
  });

  if (!found) {
    document.getElementById("AID_list_req_UL").innerHTML += `<li name="${name}">${name} 
    <button type="button" onclick="handleReqRemButton()" value="${name}">x</button></li>`
  }
}

function handleReqRemButton(){
  let child = event.target.parentNode
  let parent = event.target.parentNode.parentNode

  parent.removeChild(child)
}

function requestToJSON(){
  let legend_requests = []
  let option_RHL = null
  let option_AID = null
  let option_DYNV = null
  let option_VVrij = null
  let request_name

  ///////////////////////// LEGEND REQUESTS //////////////////////////////////
    
  if ($('ul#MSI_list_req_UL li').length >= 1) {  
    $("#MSI_list_req_UL li").each((id, elem) => {
      let selectID = "legend_selector_"+ elem.getAttribute("name")
      let e=document.getElementById(selectID)

      legend_requests.push(parseLegendRequest(elem.getAttribute("name"), e.options[e.selectedIndex].value))
    });
  }  

  //////////////////////////// REQUEST NAME /////////////////////////////////

  request_name = $("#request_name_user_input").val()
  if (request_name.length == 0) {
    let date = new Date();
    request_name = pad2(date.getHours()) + "." + pad2(date.getMinutes()) + "." + pad2(date.getSeconds())
  }
  request_name = "request_" + request_name 
  request_name.replaceAll(" ","_")

  ////////////////////////////// V-VRIJ ////////////////////////////////////

  if ($("#V-Vrij_check").is(':checked')){
    option_VVrij = []

    $("#MSI_list_req_UL li").each((id, elem) => {
      let selectID = "legend_selector_"+ elem.getAttribute("name")
      let e=document.getElementById(selectID)

      if (e.options[e.selectedIndex].value == "cross") {
        option_VVrij.push("[RSU_"+elem.getAttribute("name").replaceAll(" ","_")+"]")
      }
    })
  }  
  
  ////////////////////////////// DYN-V ////////////////////////////////////

  if ($('ul#DYNV_list_req_UL li').length >= 1){
    let dynv_rsu_list = []
    let MSI_data = JSON.parse(window.sessionStorage.getItem("MSI_data"))

    $("#DYNV_list_req_UL li").each((id, elem) => {
      let name = elem.getAttribute("name")
      let msi = "[RSU_"+name.replaceAll(" ","_")+",1]"
      MSI_data[msi]["row"].map((elem) => {
        dynv_rsu_list.push(elem)
      })
      
    });
    option_DYNV = {
      "max_speed" : parseInt($("#DYNV_selector").val()),
      "MSI" : dynv_rsu_list
    }
  }

  /////////////////////////////// RHL /////////////////////////////////////

  if ($('ul#RHL_list_req_UL li').length >= 1){
    let rhl_list = []
    $("#RHL_list_req_UL li").each((id, elem) => {
      let name = elem.getAttribute("name")
      rhl_list.push(name.replaceAll(" ","_"))
    });
    option_RHL = {
      "state" : $("#RHL_selector").val(),
      "RHL" : rhl_list
    }
  }

  /////////////////////////////// AID /////////////////////////////////////

  if ($('ul#AID_list_req_UL li').length >= 1) {  
    let aid_list = []
    $("#AID_list_req_UL li").each((id, elem) => {
      let name = elem.getAttribute("name")
      aid_list.push("RSU_"+name.replaceAll(" ","_").replace("_TS_",","))
    }); 
      
    option_AID = {
      "trafficstream" : aid_list  ,
      "speed" : parseInt($("#AID_selector").val())
      }
    };

  ///////////////////////// COMBINE AND SEND //////////////////////////////

  if (legend_requests.length >= 1 ||
    option_RHL!==null ||
    option_AID!==null ||
    option_DYNV!==null) {
    
    let options = {}
    if (option_VVrij !==null) options["V_Vrij_50"] = option_VVrij
    if (option_DYNV !==null) options["DYN-V"] = option_DYNV
    if (option_RHL !==null) options["RHL"] = option_RHL
    if (option_AID !==null) options["AID"] = option_AID

    return request = {
      "name": request_name,
      "type":"add",
      "legend_requests": legend_requests,
      "options": options
      }
  }

  return false
}

function pad2(n) { return n < 10 ? '0' + n : n }

function parseLegendRequest(RSU,legend) {
  return legendWordToLetter(legend)+"[RSU_"+RSU.replaceAll(" ","_")+"]"
}

function list_UL_search(input_id,ul_id){
  let input, filter, ul, li, a, i ,txtValue;
  input = document.getElementById(input_id);
  filter = input.value.toUpperCase();
  ul = document.getElementById(ul_id);
  li = ul.getElementsByTagName('li');

  for (i = 0; i < li.length; i++) {
    a = li[i].getElementsByTagName("button")[0];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
    } else {
      li[i].style.display = "none";
    }
  }
}