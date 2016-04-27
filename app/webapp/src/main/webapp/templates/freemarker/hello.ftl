<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#-- Template for the body of the About page -->

<h2>${siteName!}</h2>

<#if title?has_content>
    <div>${title}</div>
</#if>

<#if venueName?has_content>
    <div>${venueName}</div>
</#if>

<#if doi?has_content>
    <div>${doi}</div>
</#if>