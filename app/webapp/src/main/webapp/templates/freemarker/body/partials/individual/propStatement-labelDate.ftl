
<@showStatement statement />

<#macro showStatement statement>
    ${statement.label!}&nbsp;<#if statement.year??><span class="listDateTime">${statement.year}</span><#elseif statement.startyear?? & statement.endyear??><span class="listDateTime">${statement.startyear} - ${statement.endyear}</span><#elseif statement.endyear??><span class="listDateTime">${statement.endyear}</span><#elseif statement.dateTimeStart?? & statement.dateTimeEnd??><span class="listDateTime">${statement.dateTimeStart[0..3]} - ${statement.dateTimeEnd[0..3]}</span><#elseif statement.dateTimeEnd??><span class="listDateTime">${statement.dateTimeEnd[0..3]}</span></#if>
</#macro>
