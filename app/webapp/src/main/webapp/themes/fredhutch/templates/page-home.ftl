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
            <h2>Welcome to Fred Hutch Researcher Profiles</h2>

            <p class="under-construction" style="font-weight: bold; font-size: .97em; font-style: italic;">Site Under Construction</p>

            <p>VIVO is a research-focused discovery tool that provides detailed information about our scientists and physicians.  Learn more about our efforts to generate new scientific discoveries and translate them into effective medical practices, therapies and public health approaches.</p>

            <p>Browse or search information on people, organizations, publications and expertise.</p>

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
                            <li role="listitem"><a href="" title="http://vivoweb.org/ontology#vitroClassGrouporganizations">Organizations</a></li>
                            <li role="listitem"><a href="" title="http://vivo.fredhutch.org/individual/vitroClassGrouppublications">Publications</a></li>
                            <li role="listitem"><a href="" title="http://vivo.fredhutch.org/individual/vitroClassGroupexpertise">Expertise</a></li>                            
                        </ul>
                    </form>
                </fieldset>
            </section> <!-- #search-home -->

            <section id="recent">

            <div class="home-box" id="home-pubs">
                <h1>Recent publications</h1>
            </div>
            </section>

        <#include "footer.ftl">

    <script>
        // set the 'limmit search' text and alignment
        if  ( $('input.search-homepage').css('text-align') == "right" ) {
             $('input.search-homepage').attr("value","${i18n().limit_search} \u2192");
        }

        addRecent("pubs");

        function addRecent(name) {
            var selected = $("#home-"+ name);
            $.getJSON( "./recent/" + name, function( data ) {
                var items = [];
                $.each( data, function( key, val ) {
                    if (name != "news") {
                        url = ".." + val.url;
                    } else {
                        url = val.url;
                    }
                    items.push( "<li><a href=\"" + url + "\">" + val.name + "</a>&nbsp;<span class=\"date\">" + val.date.substring(0,7) + "</span></li>" );
                });
                $( "<ul/>", {
                    html: items.join( "" )
                }).appendTo( selected );
            });
        }
    </script>
    </body>
</html>
