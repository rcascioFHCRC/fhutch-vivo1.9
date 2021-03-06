<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#-- VIVO-specific default object property statement template.

     This template must be self-contained and not rely on other variables set for the individual page, because it
     is also used to generate the property statement during a deletion.
-->

<@showStatement statement />

<#macro showStatement statement>
    <#-- The query retrieves a type only for Persons. Post-processing will remove all but one. -->
    <a href="${profileUrl(statement.uri("award"))}" title="${i18n().name}">${statement.label!statement.localName!}</a><#if statement.org??>, <a href="${profileUrl(statement.uri("org"))}">${statement.orgName!}</a></#if><#if statement.date??>, <span class="listDateTime">${statement.date}</span></#if>
</#macro>
