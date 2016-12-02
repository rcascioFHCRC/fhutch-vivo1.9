
<@showStatement statement />

<#macro showStatement statement>
    ${statement.trainingName!}</a>&nbsp;<#if statement.date??><span class="listDateTime">${statement.date}</span><#elseif statement.dateTimeStart?? & statement.dateTimeEnd??><span class="listDateTime">${statement.dateTimeStart} - ${statement.dateTimeEnd}</span><#elseif statement.dateTimeEnd??><span class="listDateTime">${statement.dateTimeEnd}</span></#if>
</#macro>
