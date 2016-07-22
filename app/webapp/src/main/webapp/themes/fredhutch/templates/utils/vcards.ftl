<#-- Use a macro to keep variable assignments local; otherwise the values carry over to the
     next statement -->
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
