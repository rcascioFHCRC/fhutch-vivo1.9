
<@showStatement statement />

<#macro showStatement statement>
    ${statement.serviceName!}<#if statement.org??>, <a href="${profileUrl(statement.uri("org"))}">${statement.orgName}</a></#if><#if statement.journal??>, <a href="${profileUrl(statement.uri("journal"))}">${statement.journalName}</a></#if><#if statement.dateTimeStart?? & dateTimeEnd??>, <span class="listDateTime">${statement.dateTimeStart} - ${statement.dateTimeEnd}</span><#elseif statement.dateTimeStart??>, <span class="listDateTime">${statement.dateTimeStart}</span><#elseif statement.dateTimeEnd??>, <span class="listDateTime">${statement.dateTimeEnd}</span></#if>
</#macro>
