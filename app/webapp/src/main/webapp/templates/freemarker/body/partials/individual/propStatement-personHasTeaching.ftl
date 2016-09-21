
<@showStatement statement />

<#macro showStatement statement>
    ${statement.teachingName!}<#if statement.org??>, <a href="${profileUrl(statement.uri("org"))}">${statement.orgName}</a></#if><#if statement.date??>, <span class="listDateTime">${statement.date}</span></#if><#if statement.dateTimeStart?? & dateTimeEnd??>, <span class="listDateTime">${statement.dateTimeStart} - ${statement.dateTimeEnd}</span><#elseif statement.dateTimeStart??>, <span class="listDateTime">${statement.dateTimeStart}</span><#elseif statement.dateTimeEnd??>, <span class="listDateTime">${statement.dateTimeEnd}</span></#if>
</#macro>
