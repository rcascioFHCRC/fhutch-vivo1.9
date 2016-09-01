
<@showStatement statement />

<#macro showStatement statement>
    <a href="${profileUrl(statement.uri("person"))}">${statement.personName}</a>, ${statement.serviceName!}<#if statement.dateTimeStart?? & dateTimeEnd??>, <span class="listDateTime">${statement.dateTimeStart} - ${statement.dateTimeEnd}</span><#elseif statement.dateTimeStart??>, <span class="listDateTime">${statement.dateTimeStart}</span><#elseif statement.dateTimeEnd??>, <span class="listDateTime">${statement.dateTimeEnd}</span></#if>
</#macro>
