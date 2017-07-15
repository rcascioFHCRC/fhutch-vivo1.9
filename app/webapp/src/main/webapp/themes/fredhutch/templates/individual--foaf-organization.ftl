<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#-- Individual profile page template for foaf:Organization individuals (extends individual.ftl in vivo)-->

<#-- Do not show the link for temporal visualization unless it's enabled -->

<#assign affiliatedResearchAreas>
    <#include "individual-affiliated-research-areas.ftl">
</#assign>

<#include "individual.ftl">


<#-- Based of Weill Cornell VIVO publication sorting.
http://vivo.med.cornell.edu/display/cwid-ljaronne -->
<div id="pub-sorter">
  <span>Sort by</span>
  <select id="dropdown_options" class="button" title="Sort by">
      <option value="newest" selected>Newest</option>
      <option value="oldest">Oldest</option>
      <option value="pubname">Title</option>
      <option value="venue">Journal</option>
  </select>
</div>

<script>

//pub sorting - only show if there are pubs on the page
if ($('#relates-Publication-List li').length > 0) {
  var sorter = $('#pub-sorter')[0];
  $('h3#relates').append(sorter);
  $(sorter).show();

  $('#dropdown_options').change(function (e) {
        var optionSelected = $("option:selected", this);
        var valueSelected = this.value;
        //console.debug(valueSelected);
        if (valueSelected == 'oldest') {
          tinysort('div.pub-container', {attr:'datetime'},{attr:'pubname'})

        } else if (valueSelected == 'newest') {
          tinysort('div.pub-container', {attr:'datetime', order:'desc'},{attr:'pubname'})
        } else if (valueSelected == 'pubname') {
          tinysort('div.pub-container', {attr:'pubname'}, {attr:'datetime', order:'desc'})
        } else if (valueSelected == 'venue') {
          tinysort('div.pub-container', {attr:'venue'},{attr:'pubname'})
        }
  });
};

</script>


${scripts.add('<script src="${urls.base}/js/tinysort.min.js"></script>')}
