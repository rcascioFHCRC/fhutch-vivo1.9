<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#-- Template for the body of the org browse page -->

<h2>${title}</h2>



<ul class="org-browse">
<#list tree as org>
    <li><h3><a href="${org.url}">${org.name}</a></h3></li>

    <#assign kids = org.children!>
    <ul class="sub-org">
        <#list kids as sub>
            <li>
                <a href="${sub.url}">${sub.name}</a>
            </li>
        </#list>
    </ul>
</#list>
</ul>


<@dumpAll />
