<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#-- Template for the body of the org browse page -->

<#-- Check if their are sub-orgs and render tree. Else render single line-->
<#macro branch org kids>
    <#if kids?hasContent>
      <li class="top-org"><a href="${org.url}">${org.name}</a><#if kids?hasContent><span class="tree-toggler chevron bottom"></span></#if>
                <ul class="sub-org tree">
                    <#list kids as sub>
                    <#assign gkids = sub.children!>
                        <li><a href="${sub.url}">${sub.name}</a><#if gkids?hasContent><span class="tree-toggler chevron bottom"></span></#if>
                            <#if gkids?hasContent>
                                <ul class="sub-org tree">
                                    <#list gkids as sub2>
                                        <#assign ggkids = sub2.children!>
                                        <li><a href="${sub2.url}">${sub2.name}</a><#if ggkids?hasContent><span class="tree-toggler chevron bottom"></span></#if>
                                            <#if ggkids?hasContent>
                                                <ul class="sub-org tree">
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
         </li>
    <#else>
        <li class="top-org"><a href="${org.url}">${org.name}</a></li>
    </#if>
</#macro>

<div class="org-browse-header">
    <h2>${title}</h2>
    <div><a href="./organizations">Browse by organization type</a></div>
</div>

<div id="org-tree">
    <h3>Browse by organization structure</h3>
    <h4><a class="top-org" href="${topUrl}">Fred Hutchinson Cancer Research Center Leadership</a></h4>

    <h4>Divisions</h4>
    <ul>
    <#list divisions as division>
        <@branch org=division kids=division.children!/>
    </#list>
    </ul>

    <h4>Scientific Initiatives</h4>
    <ul>
    <#list sciInit as sciI>
        <@branch org=sciI kids=sciI.children!/>
    </#list>
    </ul>

    <#if irc?hasContent>
        <h4>Interdisciplinary Research Centers</h4>
        <ul>
        <#list irc as rc>
            <@branch org=rc kids=rc.children!/>
        </#list>
        </ul>
    </#if>

</div>

${scripts.add('<script type="text/javascript" src="${urls.base}/js/fhBrowse.js"></script>')}

