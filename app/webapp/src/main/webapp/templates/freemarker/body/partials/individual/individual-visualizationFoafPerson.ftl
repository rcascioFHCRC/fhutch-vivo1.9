<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#-- Template for sparkline visualization on individual profile page -->

<#-- Determine whether this person is an author -->
<#assign isAuthor = p.hasVisualizationStatements(propertyGroups, "${core}relatedBy", "${core}Authorship") />

<#if (isAuthor)>

    <#assign standardVisualizationURLRoot ="/visualization">

        <#if isAuthor>
            <#assign coAuthorIcon = "${urls.images}/visualization/coauthorship/co_author_icon.png">
            <#assign coAuthorVisUrl = individual.coAuthorVisUrl()>

            <a href="${coAuthorVisUrl}" title="${i18n().co_author_network}"><img src="${coAuthorIcon}" alt="${i18n().co_author}" width="25px" height="25px" />&nbsp;${i18n().co_author_network}</a>

        </#if>

</#if>
