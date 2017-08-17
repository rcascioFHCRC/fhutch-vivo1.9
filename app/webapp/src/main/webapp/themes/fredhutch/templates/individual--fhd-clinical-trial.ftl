<#include "individual-setup.ftl">
<#import "lib-vivo-properties.ftl" as vp>

<#assign nctp = "http://vivo.fredhutch.org/ontology/clinicaltrials#nctNumber">
<#assign furlp = "http://vivo.fredhutch.org/ontology/display#url">
<#global pg=propertyGroups>

<#-- helper to get data properties -->
<#function gdp prop>
    <#assign val = pg.getProperty(prop)!>
    <#if val?has_content>
        <#if val.statements[0]??>
            <#return val.statements[0].value>
        </#if>
    </#if>
</#function>

<#assign nct=gdp(nctp)!>
<#assign url=gdp(furlp)!>


<#assign individualProductExtension>
    <ul class="individual-urls" role="list">
        <li role="list-item">For eligibility information and additional details, visit 
        <#if nct?has_content>
            <a href="https://clinicaltrials.gov/show/${nct}" target="_blank">https://clinicaltrials.gov/show/${nct}</a>
        </#if>
        <#if url?has_content>
            <#if "https://clinicaltrials.gov/show/${nct}"!= url>
                or
                <a href="${url}" target="_blank">${url}</a>
            </#if>
        </#if>
        </li>
    </ul>
    <#include "individual-overview.ftl">
    <ul class="top-offset1 individual-urls">
        <li><a href="http://www.fredhutch.org/en/treatment/clinical-trials/patient-protection.html" target="_blank">Patient Protection Information</a></li>
    </ul>
        </section> <!-- #individual-info -->
    </section> <!-- #individual-intro -->
    <!--postindividual overiew ftl-->
</#assign>


<#-- Ontology properties -->
<#if !editable>
<#-- We don't want to see the first name and last name unless we might edit them. -->
  <#assign skipThis = propertyGroups.pullProperty(furlp)!>
</#if>

<#include "individual-vitro.ftl">

<p class="disclaimer">
Disclaimer: We update this information regularly. However, what you read today may not be completely up to date.
Please remember: Talk to your health care providers first before making decisions about your health care. Whether you are eligible for a research study depends on many things. There are specific requirements to be in research studies. These requirements are different for each study.
</p>


<script>
var i18nStrings = {
    displayLess: '${i18n().display_less}',
    displayMoreEllipsis: '${i18n().display_more_ellipsis}',
    showMoreContent: '${i18n().show_more_content}',
    verboseTurnOff: '${i18n().verbose_turn_off}',
};
</script>

${stylesheets.add('<link rel="stylesheet" href="${urls.base}/css/individual/individual-vivo.css" />')}

${headScripts.add('<script type="text/javascript" src="${urls.base}/js/jquery_plugins/jquery.truncator.js"></script>')}
${scripts.add('<script type="text/javascript" src="${urls.base}/js/individual/individualUtils.js"></script>')}


