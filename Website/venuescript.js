function httpGet()
{
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", "http://localhost:3000/venues", false); // false for synchronous request
  xmlHttp.send();
  venues = xmlHttp.responseText;

  venues_json = JSON.parse(venues);

  venues_json.forEach(function (item, index) {
  var name = item.name;
  var category = item.category;
  var ranking = item.rank_final;
  console.log(ranking);
  tr = $('<tr/>');
          tr.append("<td>" + ranking + "</td>");
          tr.append("<td>" + name + "</td>");
          tr.append("<td>" + category + "</td>");
          $('table').append(tr);
  });
} 		
	
function myFunction() {
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
