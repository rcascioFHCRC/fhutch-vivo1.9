<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#-- Template for the body of the About page -->

<h2>${siteName!}</h2>

<ul>
<#list tree as org>
    <li>${org.name}</li>
</#list>
</ul>