
<h2 class="browse-header">Explore areas of expertise</h2>
<div class="expertise aside">
<a href="./expertise">Browse by area of expertise</a>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.8.3/underscore-min.js"></script>
<script type="text/javascript" src="${urls.base}/js/d3.js"></script>
<!-- load D3plus after D3js -->
<script type="text/javascript" src="${urls.base}/js/d3plus.js"></script>


<style>
h1 {
  margin-left: auto;
  margin-right:auto;
  width: 25%;
  margin-bottom: 1em;
}
#viz {
  width: 75%;
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

</style>


<!-- create container element for visualization -->
<div id="viz">
</div>

<script>
  // sample data array
  var expertiseData = ${areas};

  function tip(point) {
    console.debug(point);
    var vivo = "./display?uri=";
    var index = _.indexOf(_.pluck(expertiseData, 'name'), point);
    var meta = expertiseData[index];
    console.debug(meta);
    var url = vivo + meta.uri;
    return "<a href=\"" + url + "\" id=\"view\">View researchers</a></h1>";
  }

  // instantiate d3plus
  var visualization = d3plus.viz()
    .container("#viz")
    .data(expertiseData)
    .type("tree_map")
    .font({"family": "\"Geogrotesque-Regular\",Arial,Helvetica,Sans-serif"})
    .id(["name"])
    .size("researchers")      // sizing of blocks
    .tooltip({"share": false, "html": tip, "large": 300, "stacked": true})
    .title({
      "sub": {
        "font": {"size": 18, "color": "navy"}
      }
    })
    .draw()
</script>
