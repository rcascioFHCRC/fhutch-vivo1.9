<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#-- Custom object property statement view for faux property "people". See the PropertyConfig.n3 file for details.

     This template must be self-contained and not rely on other variables set for the individual page, because it
     is also used to generate the property statement during a deletion.
 -->

<#import "hutch-dates.ftl" as hd>
<#import "lib-sequence.ftl" as s>
<#import "lib-datetime.ftl" as dt>

<@showPosition statement />

<#-- Use a macro to keep variable assignments local; otherwise the values carry over to the
     next statement -->
<#macro showPosition statement>
<#if statement.hideThis?has_content>
    <span class="hideThis">&nbsp;</span>
    <script type="text/javascript" >
        $('span.hideThis').parent().parent().addClass("hideThis");
        if ( $('h3#relatedBy-Position').attr('class').length == 0 ) {
            $('h3#relatedBy-Position').addClass('hiddenPeople');
        }
        $('span.hideThis').parent().remove();
    </script>
<#else>
    <#local linkedIndividual>
        <#if statement.person??>
            <a href="${profileUrl(statement.uri("person"))}" title="${i18n().person_name}">${statement.personName}</a>
        <#else>
            <#-- This shouldn't happen, but we must provide for it -->
            <a href="${profileUrl(statement.uri("position"))}" title="${i18n().missing_person_in_posn}">${i18n().missing_person_in_posn}</a>
        </#if>
    </#local>

    <#-- For these subclasses, don't show org. -->
    <#--<#assign sc = ['http://vivo.fredhutch.org/ontology/display#Membership', 'http://vivoweb.org/ontology/core#FacultyPosition', 'http://vivoweb.org/ontology/core#FacultyAdministrativePosition', 'http://vivo.fredhutch.org/ontology/display#Emeritus']>

    <#if individual.mostSpecificTypes?seq_contains("Lab")>
        <@s.join [ linkedIndividual ] /> <@hd.yearInterval "${statement.dateTimeStart!}" "${statement.dateTimeEnd!}" />
    <#else>
        <#if sc?seq_contains("${statement.subclass!}")>
             <@s.join [ linkedIndividual, statement.positionTitle! ] /> <@hd.yearInterval "${statement.dateTimeStart!}" "${statement.dateTimeEnd!}" />
        <#else>
            <@s.join [ linkedIndividual, statement.positionTitle!, statement.orgName! ] /> <@hd.yearInterval "${statement.dateTimeStart!}" "${statement.dateTimeEnd!}" />
        </#if>
    </#if>-->
<@s.join [ linkedIndividual ] />
</#if>
</#macro>
