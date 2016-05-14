<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#-- Template for the body of the org browse page -->

<h2>${title}</h2>


<ul id="person-browse"
<#list people as person>
    <li>
        <h4>
        <#if (person.picture)?hasContent>
            <img src="${person.picture}"/>
        </#if>
        ${person.name}</h4>
    </li>
    <#assign positions = person.positions!>
    <#if positions?hasContent>
    <ul class="positions">
        <#list positions as pos>
            <li>${pos.title}, <a href="${pos.url}">${pos.orgName}</a></li>
        </#list>
    </ul>
    <hr/>
    </#if>
</#list>
</ul>
