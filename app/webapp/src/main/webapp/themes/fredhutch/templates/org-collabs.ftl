

${stylesheets.add('<link rel="stylesheet" href="${urls.base}/themes/fredhutch/css/org-collab.css" />')}
${headScripts.add('<script type="text/javascript" src="${urls.base}/js/underscore-min.js"></script>')}
${headScripts.add('<script type="text/javascript" src="${urls.base}/js/handlebars.min.js"></script>')}
${headScripts.add('<script type="text/javascript" src="${urls.base}/js/d3.js"></script>')}
${headScripts.add('<script type="text/javascript" src="${urls.base}/js/d3plus.js"></script>')}

<h2 class="browse-header">${name} Collaboration Network</h2>
<div class="back-link"><a href="${urls.base}/display/${localName}">View organization page</a></div>



<#-- <p>${overview}</p> -->
<#-- <h5><a href="./${localName}" title="Click to reset visualization">Collaboration network</a></h5> -->
<div class="viz-intro">
  <p>
  This network shows collaborations among members of this organization only.
  <br/><a class="message" href="./${localName}" title="Click to reset visualization">click to reset visualization</a>
  </p>
</div>
<!-- create container element for visualization -->
<div id="viz">
</div>

<div id="table">
</div>

<script id="header-template" type="text/x-handlebars-template">
  <div class="dialog">
    <a onclick="closeTip()" class="close-thik"></a>
  </div>
  <div class="entry">
    {{# if picture }}
      <img src="{{picture}}" class="tiny-image"/>
    {{/if}}
    <h6 class="profile-card">{{name}}</h3>
    <span class="profile-card-link"><a href="{{url}}">view profile</a></span>
  </div>
</script>

<script id="table-template" type="text/x-handlebars-template">
  <table id="collab-table">
    <thead>
      <tr>
        <th>Name</th>
        <th>Total Number of Organizational Collaborators</th>
      </tr>
    </thead>
    <tbody>
    {{#each objects}}
    <tr>
      <td><a href="../display/{{id}}">{{name}}</a></td>
      <td>{{#if total }}<a href="#" onclick="loadTarget(this)" data-id="{{id}}">{{total}}{{else}}-{{/if}}</td>
    </tr>
    {{/each}}
    </tbody>
  </table>
</script>


<script>

  var baseURL="${baseURL}";

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
  var tipParams = {
    "html": tip,
    "size": true,
    "fullscreen": false,
    "large": 300,
    "stacked": true
  };

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
      makeNetworkViz(sortedData);
      addTable(data);
    });
  }


function getColor(total) {
  var colors = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"]
  return colors[Math.floor(Math.random() * colors.length)];
}


  function makeNetworkViz(data) {
    var maxTotal = _.max(data.nodes, function(object){return object.total}).total
    var third = Math.ceil(maxTotal / 3 )
    var getColor = d3.scale.linear()
      .domain([1, third, third+third, maxTotal])
      .range(['#ffffcc','#a1dab4','#41b6c4','#225ea8']);
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
      .font({ "family": "Geogrotesque-Regular"})
      .legend(false)
      //.color({"range": ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"], "value": "total"})
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
        .font({ "family": "Geogrotesque-Regular"})
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

    function closeTip() {
      d3plus.tooltip.remove();
    }
</script>
