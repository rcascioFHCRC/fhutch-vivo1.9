<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#-- Template for the body of the org browse page -->

<h2>${title}</h2>

<div class="alpha-browse">
    <p>Select a letter to display a list of researchers.</p>
    <ul>
        <#list alphabet as alpha>
        <li>
            <#if alpha == letter>
                ${alpha?upperCase}
            <#else>
                <a href="${baseUrl}/${alpha}">${alpha?upperCase}</a>
            </#if>
        </li>
        </#list>
    </ul>
</div>
<hr/>

<#-- <div class="sidebar">
    <form action="/vivo/search" name="search" role="search" accept-charset="UTF-8" method="POST">
        <fieldset>
            <legend>Search for researchers</legend>
                <input type="text" name="querytext" class="search-vivo" autocapitalize="off">
                <input type="hidden" name="type" value="http://xmlns.com/foaf/0.1/Person">
        </fieldset>
        <input type="submit" value="Search" class="search">
     </form>
</div> -->

    <div id="person-browse">
    <#list people as person>
        <div class="overview">
            <div class="img-wrapper">
                <#if (person.picture)?hasContent>
                        <img class="thumbnail img-circle" src="${person.picture}"/>
                </#if>
            </div>
            <div class="details">
                <div class="name">
                    <a href="${person.url}">${person.name}</a>
                </div>
                <#assign positions = person.positions!>
                <#if positions?hasContent>
                <div class="positions">
                    <ul>
                        <#list positions as pos>
                            <li>${pos.title}, <a href="${pos.url}">${pos.orgName}</a></li>
                        </#list>
                    </ul>
                </div>
            </div>
            <div class="clear"></div>
            </#if>
        </div>
    </#list>
    </div>
</div>
