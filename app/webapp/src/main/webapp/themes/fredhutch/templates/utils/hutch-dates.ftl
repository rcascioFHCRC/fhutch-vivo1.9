
<#-- Print date time interval as year only
Requires start to be populated.-->
<#macro yearInterval start="" end="">
<#if start?has_content><span class="listDateTime">${start?string[0..3]}<#if end?has_content> - ${end?string[0..3]}</#if></span></#if>
</#macro>
