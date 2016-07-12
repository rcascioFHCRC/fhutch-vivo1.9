<#include "individual-setup.ftl">
<#import "lib-vivo-properties.ftl" as vp>

<#assign individualProductExtension>
    <ul class="individual-urls" role="list">
        <li role="list-item"><a href="http://www.fredhutch.org/en/treatment/clinical-trials/patient-protection.html">Patient Protection</a></li>
        <#assign webpage = propertyGroups.pullProperty("http://vivo.fredhutch.org/ontology/display#url")!>
        <#if webpage?has_content>
            <li role="list-item"><a href="${webpage.statements[0].value}">${webpage.statements[0].value}</a></li>
        </#if>
    <ul>
    <br/>
    <#include "individual-overview.ftl">
    ${affiliatedResearchAreas!}
        </section> <!-- #individual-info -->
    </section> <!-- #individual-intro -->
    <!--postindividual overiew ftl-->
</#assign>

<#if individual.conceptSubclass() >
    <#assign overview = propertyGroups.pullProperty("http://www.w3.org/2004/02/skos/core#broader")!>
    <#assign overview = propertyGroups.pullProperty("http://www.w3.org/2004/02/skos/core#narrower")!>
    <#assign overview = propertyGroups.pullProperty("http://www.w3.org/2004/02/skos/core#related")!>
</#if>

<#include "individual-vitro.ftl">
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
${scripts.add('<script type="text/javascript" src="https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js"></script>')}

