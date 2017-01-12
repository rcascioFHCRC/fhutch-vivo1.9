<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#include "menupage-checkForData.ftl">



<#assign classGroup = classGroupUri?replace("http://vivo.fredhutch.org/individual/vitroClassGroup", "")>

<#if !noData>
    <section id="menupage-intro" role="region">
        <h2>${page.title}</h2>
        <#if classGroup?contains("expertise")>
            <div class="aside"><a href="./expertise-browse">Explore areas of expertise</a></div>
        </#if>
        <#if classGroup?contains("clinical")>
            <div class="aside">Visit <a href="./people-browse">people profiles</a> to see trials and studies associated with specific researchers. To search for studies and trials by keyword or topic use the search function and select the Clinical Trials filter in the drop-down list.</div>
        </#if>
        <#if classGroup?contains("InternalOrgs")>
            <div class="aside"><a href="./org-browse">Browse by organization structure</a></div>
        </#if>
    </section>

    <#include "menupage-browse.ftl">

    ${stylesheets.add('<link rel="stylesheet" href="${urls.base}/css/menupage/menupage.css" />')}

    <#include "menupage-scripts.ftl">
<#else>
    ${noDataNotification}
</#if>
