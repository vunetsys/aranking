function getContent(url){
  var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", url, false); // false for synchronous request
    xmlHttp.send();
    result = xmlHttp.responseText;
    return JSON.parse(result);
}

function changeContent(aff_id) {
  link = 'http://localhost:3000/venues/' + aff_id;
  hoverid = "hover" + aff_id;
  span = document.getElementById(hoverid);
  // span.innerHTML = "TEST: " + aff_id;
  // venues = getContent(link);
  var size = Object.keys(venues).length;

  divid = "div" + aff_id;
  html = "<div style='display: hidden' id='" + divid + "'><table><thead>Number of published venues: " + size + "</thead>"

  // span.innerHTML = "Number of published venues: " + size + "</br>"
  venues.forEach(function(item, index){
    var name = item.name;
    var rank = item.rank_final;
    html += "<tr><td>" + rank + "</td><td>" + name + "</td></tr>";
    // span.innerHTML += rank + ": " + name + "</br>";
  });
  html += "</table></div>";
  return html;
  // tr = $('</tr>')
  //     tr.append(html);
  // $('#aff_table').append(tr);
  // $(hoverid).innerHTML = "TEST!";
  // document.getElementById(aff_id).innerHTML = "TEST!";
  // document.getElementById(aff_id).style = "Color: red";

}

function makeVisible(id){
  divid = "div" + id;
  document.getElementById(divid).style.display = "block";
} 


function deleteTable(aff_id){
  hoverid = "hover" + aff_id;
  divid = "div" + aff_id;
  tableid = "table" + aff_id;

  document.getElementById(hoverid).innerHTML = "►";
  // var elem = document.getElementById(divid).remove();
  // elem.parentNode.removeChild(divid);

  // var elem = document.getElementById(tableid).remove();
  // elem.parentNode.removeChild(tableid);

  test_span = document.getElementById(hoverid);
  test_span.onclick = function() {
              generateVenuePage(aff_id);  
          }
}


function generateVenuePage(aff_id){
  link = 'http://localhost:3000/venues/' + aff_id;
  hoverid = "hover" + aff_id;
  span = document.getElementById(hoverid);
  // span.innerHTML = "TEST: " + aff_id;
  venues = getContent(link);
  var size = Object.keys(venues).length;

  divid = "div" + aff_id;
  tableid = "table" + aff_id;
  html = "▼<div></br><table id='" + tableid + "'><thead><strong>Number of published venues: </strong>" + size + "</thead>"
  // <div id='" + divid + "'>▼</div>
  // span.innerHTML = "Number of published venues: " + size + "</br>"
  venues.forEach(function(item, index){
    var name = item.name;
    var rank = item.rank_final;
    html += "<tr><td>" + rank + "</td><td>" + name + "</td></tr>";
    // span.innerHTML += rank + ": " + name + "</br>";
  });
  html += "</table></div>";
  document.getElementById(hoverid).innerHTML = html;

  test_span = document.getElementById(hoverid);
  test_span.onclick = function() {
              deleteTable(aff_id);  
          }
  return;
}

function generateVenuePage2(venueLinkUrl, uni_name){
  var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", venueLinkUrl, false); // false for synchronous request
    xmlHttp.send();
    venues = xmlHttp.responseText;
    console.log(venues)

    result_json = JSON.parse(venues);
    console.log("For university: " + uni_name);
    result_json.forEach(function(item, index){
      var name = item.name;
      var rank = item.final_rank;
      console.log(rank + ": " + name);
});
}

function httpGet()
	  {
    aff_json = getContent("http://localhost:3000/aff");   

    aff_json.forEach(function(item, index){
    var name = item.affiliation;
    var country = item.location;
    var ranking = item.rank_final;
    var id = item.id;
    var link = 'http://localhost:3000/venues/' + id;
    var hoverid = "hover" + id;
    // var venuecontent = changeContent(id);
    // console.log(venuecontent);
    // generateVenuePage(link, name);// generateVenuePage(link, name);
    tr = $('<tr/>')
            tr.append("<td>" + ranking + "</td>");
            tr.append("<td><span>" + name + " </span><span id='" + hoverid + "'>► </span></td>");
            tr.append("<td>" + country + "</td>");
            $('table').append(tr);
            // $('table').append(venuecontent);

    test_span = document.getElementById(hoverid);
    test_span.onclick = function() {
                generateVenuePage(id);  
            }
    });
    // onclick='changeContent(" + hoverid + ")'

    // onclick=loadpvenues(" + link + ")

    // var xmlHttp = new XMLHttpRequest();
    // xmlHttp.open( "GET", "http://localhost:3000/venues", false); // false for synchronous request
    // xmlHttp.send();
    // venues = xmlHttp.responseText;

    // venues_json = JSON.parse(venues);

    // venues_json.forEach(function (item, index) {
    // var name = item.name;
    // var category = item.category;
    // var ranking = item.rank_final;
    // tr = $('<tr/>');
    //         tr.append("<td>" + ranking + "</td>");
    //         tr.append("<td>" + name + "</td>");
    //         tr.append("<td>" + category + "</td>");
    //         $('table').append(tr);
    // });
	  } 		

function myFunction() {
  // Declare variables 
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("namesearch");
  filter = input.value.toUpperCase();
  table = document.getElementById("aff_table");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[1];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    } 
  }
}
function myFunction2() {
  // Declare variables 
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("locationsearch");
  filter = input.value.toUpperCase();
  table = document.getElementById("aff_table");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[2];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    } 
  }
}

function myFunction3() {
  // Declare variables 
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("namesearch");
  filter = input.value.toUpperCase();
  table = document.getElementById("venue_table");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[1];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    } 
  }
}
