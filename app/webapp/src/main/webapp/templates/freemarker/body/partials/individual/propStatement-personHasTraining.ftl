
<@showStatement statement />

<#macro showStatement statement>
    ${statement.trainingName!}</a><#if statement.dateTimeStart?? & dateTimeEnd??>, ${statement.dateTimeStart} - ${statement.dateTimeEnd}<#else><#if statement.dateTimeEnd??>, ${statement.dateTimeEnd}</#if></#if>
</#macro>
