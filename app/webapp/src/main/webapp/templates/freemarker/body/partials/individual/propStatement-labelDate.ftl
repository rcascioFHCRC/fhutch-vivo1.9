
<@showStatement statement />

<#macro showStatement statement>
    ${statement.label!}&nbsp;<#if statement.year??><span class="listDateTime">${statement.year}</span><#elseif statement.dateTimeStart?? & statement.dateTimeEnd??><span class="listDateTime">${statement.dateTimeStart} - ${statement.dateTimeEnd}</span><#elseif statement.dateTimeEnd??><span class="listDateTime">${statement.dateTimeEnd}</span></#if>
</#macro>
