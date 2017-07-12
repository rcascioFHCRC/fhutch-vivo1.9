
<h2 class="browse-header">${name}</h2>

<script type="text/javascript" src="${urls.base}/js/underscore-min.js"></script>
<script type="text/javascript" src="${urls.base}/js/handlebars.min.js"></script>
<script type="text/javascript" src="${urls.base}/js/d3.js"></script>
<!-- load D3plus after D3js -->
<script type="text/javascript" src="${urls.base}/js/d3plus.js"></script>


<style>

#viz {
  width: 90%;
  margin-left:auto;
  margin-right:auto;
  height: 800px;
  margin-bottom: 4em;
}

a#view {
    background-color: #123054;
    color: white;
    display: block;
    font-size: 1.25em;
    margin: 2em;
    padding: .5em;
    text-align: center;
    text-decoration: none;
  }

.tiny-image {
  border-radius: 50%;
  max-width: 75px;
}

h6.profile-card {
  line-height: 1em;
}

table {
  width: 80%;
  margin-left: auto;
  margin-right: auto;
}

td, th { border: 1px solid #CCC; height: 30px; } /* Make cells a bit taller */

th {
background: #F3F3F3; /* Light grey background */
font-weight: left; /* Make sure they're bold */
padding-left: 1em;
}

td {
background: #FAFAFA; /* Lighter grey background */
text-align: left; /* Center our text */
padding-left: 1em;
}

.message {
  font-variant: small-caps;
  font-size: small;
}

</style>


<#-- <p>${overview}</p> -->

<h5><a href="./${localName}" title="Click to reset visualization">Collaboration network</a></h5>
<p>
This network shows collaborations among members of this organization only.
<br/><a class="message" href="./${localName}" title="Click to reset visualization">click to reset visualization</a>
</p>
<!-- create container element for visualization -->
<div id="viz">
</div>

<div id="table">
</div>

<script id="header-template" type="text/x-handlebars-template">
  <div class="entry">
    {{# if picture }}
      <img src="{{picture}}" class="tiny-image"/>
    {{/if}}
    <h6 class="profile-card">{{name}}</h3>
    <span class="profile-card-link"><a href="{{url}}">view profile</a></span>
  </div>
</script>

<script id="table-template" type="text/x-handlebars-template">
  <table>
    <tr>
      <th>Name</th>
      <th>Organizational Collaborators</th>
    </tr>
    {{#each objects}}
    <tr>
      <td><a href="../display/{{id}}">{{name}}</a></td>
      <td>{{#if total }}<a href="#" onclick="loadTarget(this)" data-id="{{id}}">{{total}}{{else}}0{{/if}}</td>
    </tr>
    {{/each}}
  </table>
</script>


<script>

  var baseURL="${baseURL}";
  console.debug(baseURL);

  function applyTemplate(item) {
            var source   = document.getElementById("header-template").innerHTML;
            var template = Handlebars.compile(source);
            var html    = template(item);
            return html;
        }


  function getCard(local) {
    var apiURL = baseURL + '/vds/researcher/' + local;
    d3.json(apiURL, function(error, data) {
      var card = applyTemplate(data.profile);
      document.getElementsByClassName("d3plus_tooltip_header")[0].innerHTML = card;
    });
  }

  function addTable(data) {
    var source   = document.getElementById("table-template").innerHTML;
    var template = Handlebars.compile(source);
    var cData = _.map(data.nodes, function(n) {
      if ( n.total == 0 ) {
        n.total = null;
      }
      return n;
    });
    var html = template({objects: _.sortBy(cData, function(o) { return -o.total; })});
    document.getElementById("table").innerHTML = html;

  }

  function label(data) {
    return data.name.slice(0, 125)
  }

  function tip(point) {
      getCard(point)

  }
  var tipParams = {"html": tip, "size": true, "fullscreen": false, "large": 300, "stacked": true};

  var incomingResearcher = getURLParameter("profile");
  var incomingOrg = document.location.pathname.replace(baseURL, "").split("/")[2];

  if (null === incomingResearcher)  {
    make_network(incomingOrg);
  } else {
    makeRings(incomingOrg, incomingResearcher);
  }

  function make_network(org) {
    d3.json(baseURL + "/vds/collaborations/" + org, function(error, data) {
      if (error) return console.error(error);
      make_viz(data);
      addTable(data);
    });
  }




  function make_viz(data) {
    var maxTotal = _.max(data.nodes, function(object){return object.total}).total
    var getColor = d3.scale.linear().domain([0,maxTotal])
      .range(['#ffffe0', '#8b0000']);
    var visualization = d3plus.viz()
      .container("#viz")
      .type("network")
      .data({"value": data.nodes})
      .size("total")
      .edges({
        "value": data.edges,
      })
      .color(function(d){
        return getColor(d.total);
      })
      .tooltip(tipParams)
      .text("name")
      .draw()
    };

    function makeRings(org, localName) {
      d3.json(baseURL + "/vds/collaborations/" + org, function(error, data) {
      if (error) return console.error(error);
        make_rings(data, localName);
        addTable(data);
      });
    }

    function make_rings(data, localName) {

      var visualization = d3plus.viz()
        .container("#viz")
        .type("rings")
        .data({"value": data.nodes})
        .edges({
          "label": "strength",
          "value": data.edges,
        })
        .focus(localName)
        .tooltip(tipParams)
        .text("name")
        .draw()
  };

  function loadTarget(event) {
    //console.debug(event);
    window.location.search = "?profile=" + event.getAttribute("data-id");
    return false;
  }

    function getURLParameter(name) {
      return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [null, ''])[1].replace(/\+/g, '%20')) || null;
    }
</script>
