<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#--
    Individual profile page template for foaf:Person individuals. This is the default template for foaf persons
    in the Wilma theme and should reside in the themes/wilma/templates directory.
-->

<#include "individual-setup.ftl">
<#import "lib-vivo-properties.ftl" as vp>
<#import "utils/vcards.ftl" as vc>
<#--Number of labels present-->
 <#if !labelCount??>
     <#assign labelCount = 0 >
 </#if>
<#--Number of available locales-->
 <#if !localesCount??>
   <#assign localesCount = 1>
 </#if>
<#--Number of distinct languages represented, with no language tag counting as a language, across labels-->
<#if !languageCount??>
  <#assign languageCount = 1>
</#if>
<#assign visRequestingTemplate = "foaf-person-wilma">
<#assign imageProp = "http://vivo.fredhutch.org/ontology/display#image">
<#assign orcidProp = "http://vivo.fredhutch.org/ontology/display#orcid">
<#assign localCoauthorProp = "http://vivo.fredhutch.org/ontology/display#hasLocalCoauthor">
<#assign constructionProp = "http://vivo.fredhutch.org/ontology/display#underConstruction">
<#assign piProp = "http://vivo.fredhutch.org/ontology/display#PIof">

<#assign vcardName = propertyGroups.pullProperty("http://purl.obolibrary.org/obo/ARG_2000028","http://www.w3.org/2006/vcard/ns#Name")!>
<#assign vcardPhone = propertyGroups.pullProperty("http://purl.obolibrary.org/obo/ARG_2000028","http://www.w3.org/2006/vcard/ns#Telephone")!>
<#assign primaryEmail = propertyGroups.pullProperty("http://purl.obolibrary.org/obo/ARG_2000028","http://www.w3.org/2006/vcard/ns#Work")!>

<section itemscope itemtype="http://schema.org/Person" id="individual-intro" class="vcard person" role="region">

    <section id="share-contact" role="region">
        <!-- Image -->
        <#assign img = propertyGroups.getProperty(imageProp)!>
        <#if img?has_content> <#-- true when the property is in the list, even if not populated (when editing) -->
          <#if img.statements[0]??>
            <div id="photo-wrapper">
              <img class="individual-photo" src="${img.statements[0].value}"/>
            </div>
          </#if>
        <#else>
        <img class="individual-photo" src="${placeholderImageUrl(individual.uri)}" title = "${i18n().no_image}" alt="${i18n().placeholder_image}" width="${imageWidth!}" />
        </#if>
        <!-- Contact Info -->
        <ul id="contacts">
            <#if vcardPhone?has_content>
                <#if vcardPhone.statements?has_content>
                  <#list vcardPhone.statements as statement>
                      <li class="person-contact">${statement.number!}</li>
                  </#list>
                </#if>
            </#if>
            <#if primaryEmail?has_content>
                <#if primaryEmail.statements?has_content>
                <#list primaryEmail.statements as statement>
                    <li class="person-contact"><img src="../images/emailIconSmall.gif"/>${statement.emailAddress!}</li>
                </#list>
            </#if>
            </#if>
              <!-- orcid -->
              <#assign orcid = propertyGroups.getProperty(orcidProp)!>
              <#if orcid?has_content>
                <#if orcid.statements[0]??>
                  <li class="person-contact"><img src="../images/orcid.png"><a href="https://orcid.org/${orcid.statements[0].value}" target="_blank">${orcid.statements[0].value}</a></li>
                </#if>
              </#if>

      <!-- Websites -->
      <#include "individual-webpage.ftl">
    
      <!-- localCa -->
      <#assign lca = propertyGroups.getProperty(localCoauthorProp)!>
      <#if lca?has_content>
      <#if lca.statements[0]??>
        <#if (lca.statements[0].value) != "false">
          <li class="ca-network">
          <#include "utils/coauthor-viz.ftl">
          </li>
        </#if>

        </#if>
      </#if>
        </ul>     
    </section>

    <section id="individual-info" ${infoClass!} role="region">
        <#include "individual-adminPanel.ftl">

        <header>
            <#if relatedSubject??>
                <h2>${relatedSubject.relatingPredicateDomainPublic} ${i18n().indiv_foafperson_for} ${relatedSubject.name}</h2>
                <p><a href="${relatedSubject.url}" title="${i18n().indiv_foafperson_return}">&larr; ${i18n().indiv_foafperson_return} ${relatedSubject.name}</a></p>
            <#else>
                <h1 class="vcard foaf-person">
                    <#-- Label -->
                    <span itemprop="name" class="fn"><@p.label individual editable labelCount localesCount/></span>

                    <#--  Display preferredTitle if it exists; otherwise mostSpecificTypes -->
                    <#assign title = propertyGroups.pullProperty("http://purl.obolibrary.org/obo/ARG_2000028","http://www.w3.org/2006/vcard/ns#Title")!>
                    <#if title?has_content> <#-- true when the property is in the list, even if not populated (when editing) -->
                        <#if (title.statements?size < 1) >
                            <@p.addLinkWithLabel title editable />
                        <#elseif editable>
                            <h2>${title.name?capitalize!}</h2>
                            <@p.verboseDisplay title />
                        </#if>
                        <#list title.statements as statement>
                            <span itemprop="jobTitle" class="display-title<#if editable>-editable</#if>">${statement.preferredTitle}</span>
                            <@p.editingLinks "${title.localName}" "${title.name}" statement editable title.rangeUri />
                        </#list>
                    </#if>
                </h1>
            </#if>
            <!-- Positions -->
            <#include "person-positions.ftl">
        </header>

        <!-- Overview -->
        <#include "individual-overview.ftl">
        <!-- Research Areas -->
        <#include "individual-researchAreas.ftl">
        <!-- Geographic Focus -->
        <#include "individual-geographicFocus.ftl">
    </section>

</section>

<#assign nameForOtherGroup = "${i18n().other}">

<#-- Ontology properties -->
<#if !editable>
<#-- We don't want to see the first name and last name unless we might edit them. -->
  <#assign skipThis = propertyGroups.pullProperty("http://xmlns.com/foaf/0.1/firstName")!>
  <#assign skipThis = propertyGroups.pullProperty("http://xmlns.com/foaf/0.1/lastName")!>
  <#assign skipThis = propertyGroups.pullProperty(imageProp)!>
  <#assign skipThis = propertyGroups.pullProperty (constructionProp)!>
  <#assign skipThis = propertyGroups.pullProperty(orcidProp)!>
  <#assign skipThis = propertyGroups.pullProperty(localCoauthorProp)!>
  <#assign skipThis = propertyGroups.pullProperty("http://vivo.fredhutch.org/ontology/display#briefDescription")!>
  <#assign skipThis = propertyGroups.pullProperty("http://vivo.fredhutch.org/ontology/display#nickname")!>
  <#assign skipThis = propertyGroups.pullProperty(piProp)!>
</#if>

<!-- Property group menu or tabs -->
<#--
     With release 1.6 there are now two types of property group displays: the original property group
     menu and the horizontal tab display, which is the default. If you prefer to use the property
     group menu, simply substitute the include statement below with the one that appears after this
     comment section.

     <#include "individual-property-group-menus.ftl">
-->

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


<#include "individual-property-group-tabs.ftl">

<#assign rdfUrl = individual.rdfUrl>

<#if rdfUrl??>
    <script>
        var individualRdfUrl = '${rdfUrl}';
    </script>
</#if>

<script>
    var imagesPath = '${urls.images}';
  var individualUri = '${individual.uri!}';
  var individualPhoto = '${individual.thumbNail!}';
  var exportQrCodeUrl = '${urls.base}/qrcode?uri=${individual.uri!}';
  var baseUrl = '${urls.base}';
    var i18nStrings = {
        displayLess: '${i18n().display_less}',
        displayMoreEllipsis: '${i18n().display_more_ellipsis}',
        showMoreContent: '${i18n().show_more_content}',
        verboseTurnOff: '${i18n().verbose_turn_off}',
        researchAreaTooltipOne: '${i18n().research_area_tooltip_one}',
        researchAreaTooltipTwo: '${i18n().research_area_tooltip_two}'
    };
    var i18nStringsUriRdf = {
        shareProfileUri: '${i18n().share_profile_uri}',
        viewRDFProfile: '${i18n().view_profile_in_rdf}',
        closeString: '${i18n().close}'
    };
    //replace video links with
    var videos = $('h3#video').siblings('ul').children();
    $.each(videos, function(idx, item){
      var link = $(item).text().trim();
      $(item).html("<li class=\"embed-video\"><iframe width=\"560px\" height=\"315\" src=\"" + link + "\"/></li>");
    });

    //pub sorting - only show if there are pubs on the page
    if ($('#relatedBy-Authorship-List li').length > 0) {
      var sorter = $('#pub-sorter')[0];
      $('h3#relatedBy-Authorship').append(sorter);
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

${stylesheets.add('<link rel="stylesheet" href="${urls.base}/css/individual/individual.css" />',
                  '<link rel="stylesheet" href="${urls.base}/css/individual/individual-vivo.css" />',
                  '<link rel="stylesheet" href="${urls.base}/js/jquery-ui/css/smoothness/jquery-ui-1.8.9.custom.css" />')}

${headScripts.add('<script type="text/javascript" src="${urls.base}/js/tiny_mce/tiny_mce.js"></script>',
                  '<script type="text/javascript" src="${urls.base}/js/jquery_plugins/qtip/jquery.qtip-1.0.0-rc3.min.js"></script>',
                  '<script type="text/javascript" src="${urls.base}/js/jquery_plugins/jquery.truncator.js"></script>')}

${scripts.add('<script type="text/javascript" src="${urls.base}/js/individual/individualUtils.js"></script>',
              '<script type="text/javascript" src="${urls.base}/js/individual/individualQtipBubble.js"></script>',
              '<script type="text/javascript" src="${urls.base}/js/individual/individualUriRdf.js"></script>',
        '<script type="text/javascript" src="${urls.base}/js/individual/moreLessController.js"></script>',
              '<script type="text/javascript" src="${urls.base}/js/jquery-ui/js/jquery-ui-1.8.9.custom.min.js"></script>',
              '<script type="text/javascript" src="${urls.base}/js/imageUpload/imageUploadUtils.js"></script>')}

${scripts.add('<script src="${urls.base}/js/tinysort.min.js"></script>')}
