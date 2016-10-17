<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#-- Custom object property statement view for faux property "selected publications". See the PropertyConfig.3 file for details.

     This template must be self-contained and not rely on other variables set for the individual page, because it
     is also used to generate the property statement during a deletion.
 -->

<#import "lib-sequence.ftl" as s>
<#import "lib-datetime.ftl" as dt>

<@showAuthorship statement />

<#-- Use a macro to keep variable assignments local; otherwise the values carry over to the
     next statement -->
<#macro showAuthorship statement>
<#if statement.hideThis?has_content>
    <span class="hideThis">&nbsp;</span>
    <script type="text/javascript" >
        $('span.hideThis').parent().parent().addClass("hideThis");
        if ( $('h3#relatedBy-Authorship').attr('class').length == 0 ) {
            $('h3#relatedBy-Authorship').addClass('hiddenPubs');
        }
        $('span.hideThis').parent().remove();
    </script>
<#else>
    <#local citationDetails>
            <#if statement.journal??>
                <em>${statement.journal!}</em>.
                <#if statement.volume??>${statement.volume}</#if><#if statement.issue??>, ${statement.issue}</#if><#if statement.startPage?? && statement.endPage??>. p. ${statement.startPage!}-${statement.endPage!}<#elseif statement.startPage??> p. ${statement.startPage!}</#if>.
            </#if>
    </#local>

    <#local resourceTitle>
        <#if statement.infoResource??>
            <#if citationDetails?has_content>
                <a href="${profileUrl(statement.uri("infoResource"))}"  title="${i18n().resource_name}">${statement.infoResourceName}</a>.&nbsp;
            <#else>
                <a href="${profileUrl(statement.uri("infoResource"))}"  title="${i18n().resource_name}">${statement.infoResourceName}</a>
            </#if>
        <#else>
            <#-- This shouldn't happen, but we must provide for it -->
            <a href="${profileUrl(statement.uri("authorship"))}" title="${i18n().missing_info_resource}">${i18n().missing_info_resource}</a>
        </#if>
    </#local>

    <div class="pub-container">
        <div class="title">${resourceTitle} <span class="pub-date"><@dt.yearSpan "${statement.dateTime!}" /></span></div>
        <#if statement.authorList?has_content>
            <div class="author-list">
            <#assign shortauthors=(statement.authorList)>
                <#if shortauthors?length &lt; 50>
                ${shortauthors}
                <#else>
                ${shortauthors?substring(0,50)} ...
            </#if>
            </div>
        </#if>
        ${citationDetails}
        <div class="pub-ids">
            <#if statement.doi?has_content>
                <span class="pub-id-link">Full Text via DOI:&nbsp;<a href="http://doi.org/${statement.doi}"  title="Full Text via DOI" target="external">${statement.doi}</a></span>
            </#if>
            <#if statement.pmid?has_content>
                <span class="pub-id-link">PMID:&nbsp;<a href="http://pubmed.gov/${statement.pmid}"  title="View in PubMed" target="external">${statement.pmid}</a></span>
            </#if>
            <#if statement.pmcid?has_content>
                <span class="pub-id-link">PMCID:&nbsp;<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/${statement.pmcid}"  title="View in PubMed Central" target="external">${statement.pmcid}</a></span>
            </#if>
            <#if statement.wosId?has_content>
                <#-- Change WoS link to match customer code -->
                <span class="pub-id-link">Web of Science:&nbsp;<a href="http://gateway.webofknowledge.com/gateway/Gateway.cgi?GWVersion=2&SrcApp=VIVO&SrcAuth=TRINTCEL&KeyUT=WOS:${statement.wosId}&DestLinkType=FullRecord&DestApp=WOS_CPL"  title="View in Web of Science" target="external">${statement.wosId}</a></span>
            </#if>
            <#if statement.repoURL?has_content>
                <span class="pub-id-link">Full Text via Intranet&nbsp;<a href="${statement.repoURL}"  title="View in Web of Science" target="external">${statement.repoURL}</a></span>
            </#if>
        </div>
    </div>
</#if>
</#macro>
