<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#-- Template for the body of the org browse page -->

<h2>${title}</h2>



<ul class="org-browse tree-list">
<#list tree as org>
    <li>
        <h3>
            <a href="${org.url}">${org.name}</a>
        </h3>
    </li>
    <#assign kids = org.children!>
    <ul class="sub-org">
        <#list kids as sub>
        <#assign gkids = sub.children!>
            <li>
                <a href="${sub.url}">${sub.name}</a>
                <#if gkids?hasContent>
                    <ul class="sub-org">
                        <#list gkids as sub2>
                            <#assign ggkids = sub2.children!>
                            <li>
                                <a href="${sub2.url}">${sub2.name}</a>
                                <#if ggkids?hasContent>
                                    <ul class="sub-org">
                                        <#list ggkids as sub3>
                                            <li>
                                                <a href="${sub3.url}">${sub3.name}</a>
                                            </li>
                                        </#list>
                                    </ul>
                                </#if>
                            </li>
                        </#list>
                    </ul>
                </#if>
            </li>
        </#list>
    </ul>

</#list>
</ul>
