<#-- Determine whether this person is an author -->
<#assign isAuthor = p.hasVisualizationStatements(propertyGroups, "${core}relatedBy", "${core}Authorship") />

<#if (isAuthor)>

    <#assign standardVisualizationURLRoot ="/visualization">

        <#if isAuthor>
            <#-- <#assign coAuthorIcon = "${urls.images}/visualization/coauthorship/co_author_icon.png"> -->
            <#assign coAuthorVisUrl = individual.coAuthorVisUrl()>

            <a href="${coAuthorVisUrl}" title="${i18n().co_author_network}">${i18n().co_author_network}</a>

        </#if>

</#if>
