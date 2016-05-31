<#-- $This file is distributed under the terms of the license in /doc/license.txt$  -->

<@widget name="login" include="assets" />

<#--
        With release 1.6, the home page no longer uses the "browse by" class group/classes display.
        If you prefer to use the "browse by" display, replace the import statement below with the
        following include statement:

            <#include "browse-classgroups.ftl">

        Also ensure that the homePage.geoFocusMaps flag in the runtime.properties file is commented
        out.
-->
<#import "lib-home-page.ftl" as lh>

<!DOCTYPE html>
<html lang="en">
    <head>
        <#include "head.ftl">
    </head>

    <body class="${bodyClasses!}" onload="${bodyOnload!}">
    <#-- supplies the faculty count to the js function that generates a random row number for the search query -->
        <@lh.facultyMemberCount  vClassGroups! />
        <#include "identity.ftl">

        <#include "menu.ftl">

        <section id="intro" role="region">
            <h2>Welcome to FredHutch-VIVO</h2>

            <p>VIVO is a research-focused discovery tool that provides detailed information about our scientists and physicians.  Learn more about our efforts to generate new scientific discoveries and translate them into effective medical practices, therapies and public health approaches.</p>

            <p>Browse or search information on people, departments, expertise, clinical trials, grants, and publications.</p>

        </section>

        <section id="search-home" role="region">
                <h3><span class="search-filter-selected">filteredSearch</span></h3>

                <fieldset>
                    <legend>${i18n().search_form}</legend>
                    <form id="search-homepage" action="${urls.search}" name="search-home" role="search" method="post" >
                        <div id="search-home-field">
                            <input type="text" name="querytext" class="search-homepage" value="" autocapitalize="off" />
                            <input type="submit" value="${i18n().search_button}" class="search" />
                            <input type="hidden" name="classgroup"  value="" autocapitalize="off" />
                        </div>

                        <a class="filter-search filter-default" href="#" title="${i18n().intro_filtersearch}">
                            <span class="displace">${i18n().intro_filtersearch}</span>
                        </a>

                        <ul id="filter-search-nav">
                            <li><a class="active" href="">${i18n().all_capitalized}</a></li>
                            <li role="listitem"><a href="" title="http://vivoweb.org/ontology#vitroClassGrouppeople">People</a></li>
                            <li role="listitem"><a href="" title="http://vivoweb.org/ontology#vitroClassGrouporganizations">Organizations</a>
                            </li>
                            <li role="listitem"><a href="" title="http://vivo.fredhutch.org/individual/vitroClassGrouppublications">Publications</a></li>
                            <li role="listitem"><a href="" title="http://vivo.fredhutch.org/individual/vitroClassGroupexpertise">Expertise</a></li>
                            <li role="listitem"><a href="" title="http://vivo.fredhutch.org/individual/vitroClassGroupclinicaltrials">Clinical trials</a></li>
                            <li role="listitem"><a href="" title="http://vivo.fredhutch.org/individual/vitroClassGroupNews">News</a></li>

                        </ul>
                    </form>
                </fieldset>
            </section> <!-- #search-home -->
        <#include "footer.ftl">

    <script>
        // set the 'limmit search' text and alignment
        if  ( $('input.search-homepage').css('text-align') == "right" ) {
             $('input.search-homepage').attr("value","${i18n().limit_search} \u2192");
        }
    </script>
    </body>
</html>
