<#-- Publication pages -->
<#include "individual-setup.ftl">
<#import "lib-microformats.ftl" as mf>

<#assign doip = "http://purl.org/ontology/bibo/doi">
<#assign pmidp = "http://purl.org/ontology/bibo/pmid">
<#assign wosp = "http://localhost/ontology/converis#wosId">
<#global pg=propertyGroups>

<#-- helper to get data properties -->
<#function gdp prop>
    <#assign val = pg.getProperty(prop)!>
    <#if val?has_content>
        <#if val.statements[0]??>
            <#return val.statements[0].value>
        </#if>
    </#if>
</#function>


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

<#-- Default individual profile page template -->
<#--@dumpAll /-->
<section id="individual-intro" class="vcard" role="region" <@mf.sectionSchema individual/>>
    <section id="share-contact" role="region">
        <#-- No images -->
    </section>
    <!-- start section individual-info -->
    <section id="individual-info" ${infoClass!} role="region">
        <#include "individual-adminPanel.ftl">

        <#if individualProductExtensionPreHeader??>
            ${individualProductExtensionPreHeader}
        </#if>

        <header>
            <#if relatedSubject??>
                <h2>${relatedSubject.relatingPredicateDomainPublic} for ${relatedSubject.name}</h2>
                <p><a href="${relatedSubject.url}" title="${i18n().return_to(relatedSubject.name)}">&larr; ${i18n().return_to(relatedSubject.name)}</a></p>
            <#else>
                <h1 class="fn" itemprop="name">
                    <#-- Label -->
                    <@p.label individual editable labelCount localesCount languageCount/>

                    <#--  Most-specific types -->
                    <@p.mostSpecificTypes individual />
                </h1>
            </#if>
        </header>

    <#if individualProductExtension??>
        ${individualProductExtension}
    <#else>
            </section> <!-- individual-info -->
        </section> <!-- individual-intro -->
    </#if>

<#assign nameForOtherGroup = "${i18n().other}">


<#assign doi=gdp(doip)!>
<#assign pmid=gdp(pmidp)!>
<#assign wosId=gdp(wosp)!>

<div class="pub-ids">
    <#if doi?has_content>
        <span class="pub-id-link">Full Text via DOI:&nbsp;<a href="http://doi.org/${doi}"  title="Full Text via DOI" target="external">${doi}</a></span>
    </#if>
    <#if pmid?has_content>
        <span class="pub-id-link">PMID:&nbsp;<a href="http://pubmed.gov/${pmid}"  title="View in PubMed" target="external">${pmid}</a></span>
    </#if>
    <#if wosId?has_content>
        <#-- Change WoS link to match customer code -->
        <span class="pub-id-link">Web of Science:&nbsp;<a href="http://gateway.webofknowledge.com/gateway/Gateway.cgi?GWVersion=2&SrcApp=VIVO&SrcAuth=TRINTCEL&KeyUT=WOS:${wosId}&DestLinkType=FullRecord&DestApp=WOS_CPL"  title="View in Web of Science" target="external">${wosId}</a></span>
    </#if>
</div>

<!-- Property group menu or tabs -->
<#--
    With release 1.6 there are now two types of property group displays: the original property group
     menu and the horizontal tab display, which is the default. If you prefer to use the property
     group menu, simply substitute the include statement below with the one that appears after this
     comment section.

     <#include "individual-property-group-menus.ftl">
-->

<#include "individual-property-group-tabs.ftl">


${stylesheets.add('<link rel="stylesheet" href="${urls.base}/css/individual/individual.css" />')}

${headScripts.add('<script type="text/javascript" src="${urls.base}/js/jquery_plugins/qtip/jquery.qtip-1.0.0-rc3.min.js"></script>',
                  '<script type="text/javascript" src="${urls.base}/js/tiny_mce/tiny_mce.js"></script>')}

${scripts.add('<script type="text/javascript" src="${urls.base}/js/individual/moreLessController.js"></script>')}

<script type="text/javascript">
    i18n_confirmDelete = "${i18n().confirm_delete}"
</script>


${scripts.add('<script type="text/javascript" src="https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js"></script>')}
