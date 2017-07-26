<#import "hutch-dates.ftl" as hd>
<@showStatement statement />

<#macro showStatement statement>
    ${statement.label!}&nbsp;<#if statement.dateTimeStart??><@hd.yearInterval "${statement.dateTimeStart!}" "${statement.dateTimeEnd!}" /><#else><@hd.year "${statement.date!}" /></#if>
</#macro>

