<#-- Some vcard related helpers -->
<#macro showFullName statement>
    <#if statement.fullName?has_content>
        <#if statement.prefix??><span itemprop="honorificPrefix">${statement.prefix!}</span></#if>
        <span itemprop="givenName">${statement.firstName!}</span>
        <#if statement.nickname??>
            (${statement.nickname!})
        </#if>
        <span itemprop="additionalName">${statement.middleName!}</span>
        <span itemprop="familyName">${statement.lastName!}</span><#if statement.suffix??>, ${statement.suffix!}</#if>
    </#if>
</#macro>

<#macro showPreferredName statement>
    <#if statement.fullName?has_content>
        <span itemprop="familyName">${statement.lastName!}, </span>
        <#if statement.nickname??>
            ${statement.nickname!}
		<#else>
			<span itemprop="givenName">${statement.firstName!}</span>
			<span itemprop="additionalName"> ${statement.middleName!}</span>
        </#if>		
    </#if>
</#macro>

<#macro showEmail primaryEmail>
    <#if primaryEmail.statements?has_content>
        <#list primaryEmail.statements as statement>
            <li class="person-contact"><img src="../images/emailIconSmall.gif"/>${statement.emailAddress!}</li>
        </#list>
    </#if>
</#macro>

<#macro showPhone statement>
    <#if statement.telephone?has_content>
        ${statement.telephone!}
    </#if>
</#macro>
