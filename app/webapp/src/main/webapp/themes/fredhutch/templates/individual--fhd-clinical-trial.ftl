<#include "individual-setup.ftl">
<#import "lib-vivo-properties.ftl" as vp>

<#assign individualProductExtension>
    <ul class="individual-urls" role="list">
        <#assign webpage = propertyGroups.pullProperty("http://vivo.fredhutch.org/ontology/display#url")!>
        <#if webpage?has_content>
            <li role="list-item">For eligibility information and additional details, visit: <a href="${webpage.statements[0].value}">${webpage.statements[0].value}</a></li>
        </#if>
    </ul>
    <#include "individual-overview.ftl">
    <ul class="top-offset1 individual-urls">
        <li><a href="http://www.fredhutch.org/en/treatment/clinical-trials/patient-protection.html">Patient Protection Information</a></li>
    </ul>
    ${affiliatedResearchAreas!}
        </section> <!-- #individual-info -->
    </section> <!-- #individual-intro -->
    <!--postindividual overiew ftl-->
    <p class="disclaimer">
    Disclaimer: We update this information regularly. However, what you read today may not be completely up to date.
    Please remember: Talk to your health care providers first before making decisions about your health care. Whether you are eligible for a research study depends on many things. There are specific requirements to be in research studies. These requirements are different for each study.
    </p>
</#assign>

<#if individual.conceptSubclass() >
    <#assign overview = propertyGroups.pullProperty("http://www.w3.org/2004/02/skos/core#broader")!>
    <#assign overview = propertyGroups.pullProperty("http://www.w3.org/2004/02/skos/core#narrower")!>
    <#assign overview = propertyGroups.pullProperty("http://www.w3.org/2004/02/skos/core#related")!>
</#if>

<#include "individual-vitro.ftl">

