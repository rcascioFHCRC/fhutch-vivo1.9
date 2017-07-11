
<@showStatement statement />

<#macro showStatement statement>
    ${statement.serviceName!}<#if statement.org??>, <a href="${profileUrl(statement.uri("org"))}">${statement.orgName}</a></#if><#if statement.parentOrg??>, <a href="${profileUrl(statement.uri("parentOrg"))}">${statement.parentOrgName}</a></#if><#if statement.grandParentOrg??>, <a href="${profileUrl(statement.uri("grandParentOrg"))}">${statement.grandParentOrgName}</a></#if><#if statement.journal??>, <a href="${profileUrl(statement.uri("journal"))}">${statement.journalName}</a></#if><#if statement.startyear?? & statement.endyear??>, <span class="listDateTime">${statement.startyear} - ${statement.endyear}</span><#elseif statement.startyear??>, <span class="listDateTime">${statement.startyear}</span><#elseif statement.endyear??>, <span class="listDateTime">${statement.endyear}</span></#if>
</#macro>
