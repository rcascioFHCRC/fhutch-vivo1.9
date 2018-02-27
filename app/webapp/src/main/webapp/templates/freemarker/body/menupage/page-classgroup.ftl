<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#include "menupage-checkForData.ftl">



<#assign classGroup = classGroupUri?replace("http://vivo.fredhutch.org/individual/vitroClassGroup", "")>

<#if !noData>
    <section id="menupage-intro" role="region">
        <h2>${page.title}</h2>
        <#if classGroup?contains("expertise")>
            <div class="aside"><a href="./expertise-browse">Explore a treemap graphic of expertise terms</a></div>
        </#if>
        <#if classGroup?contains("clinical")>
            <div class="aside">Visit <a href="./people-browse">people profiles</a> to see trials and studies associated with specific researchers.</div>
        </#if>
        <#if classGroup?contains("org")>
            <div class="aside"><a href="${urls.base}/org/c638881">View Fred Hutchinson Organization Page</a></div>
            <div class="aside"><a href="${urls.base}/org-browse">Browse Organizational Structure</a></div>
        </#if>
    </section>

    <#include "menupage-browse.ftl">

    ${stylesheets.add('<link rel="stylesheet" href="${urls.base}/css/menupage/menupage.css" />')}

    <#include "menupage-scripts.ftl">
<#else>
    ${noDataNotification}
</#if>
