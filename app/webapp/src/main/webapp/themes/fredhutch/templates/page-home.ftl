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
        <#include "navigation.ftl">
        <#include "menu.ftl">

        <section id="search-home" role="region">
                <h3><span class="search-filter-selected">filteredSearch</span></h3>

                <fieldset>
                    <legend>${i18n().search_form}</legend>
                    <form id="search-homepage" action="${urls.search}" name="search-home" role="search" method="post" >
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
                        <div id="search-home-field">
                            <input type="text" name="querytext" class="search-homepage" value="" autocapitalize="off" />
                            <input type="submit" value="${i18n().search_button}" class="search" />
                            <input type="hidden" name="classgroup"  value="" autocapitalize="off" />
                        </div>

                    </form>
                </fieldset>
            </section> <!-- #search-home -->


        <section id="intro" role="region">
            <h1>Welcome to <strong>Fred Hutch Scientific Profiles</strong> website,<br /> a portal that enables collaboration among researchers.</h2>
        </section>

        <section id="fhsp-desc">
            <div id="scroll-ahead"><span>Scroll Ahead</span></div>
            <div id="fhcp-is">
                <h1>Fred Hutch Scientific Profiles is:</h1>
                <div class="fhcp-is-block"><h2>For Faculty</h2>
                    <p>Need to update your faculty profile?<br/><a href="mailto:library@fredhutch.org">Click here</a> to find out how.</p>
                </div>
                <div class="fhcp-is-block"><h2>For Industry Collaboration</h2>
                    <p>Lorem ipsum dolor sit amet, consectetur elit.<br/><a href="#" target="_blank">Proin vulputate</a> sagittis metus.</p>
                </div>
                <div class="fhcp-is-block"><h2>For Journalists</h2>
                    <p>Lorem ipsum dolor sit amet, consectetur elit.<br/>Proin <a href="#" target="_blank">vulputate sagittis metus</a>.</p>
                </div>
            </div>
        </section>        

        <section id="recent">
            <div class="home-box" id="home-pubs">
                <h1>Recent publications</h1>
            </div>
        </section>

        <#include "footer.ftl">

    <script>
        // set the 'limit search' text and alignment
//        if  ( $('input.search-homepage').css('text-align') == "right" ) {
//             $('input.search-homepage').attr("value","${i18n().limit_search} \u2192");
//        }

        // set the 'prompt search' text
        if  ( $('input.search-homepage').css('text-align') == "right" ) {
             $('input.search-homepage').attr("value","${i18n().prompt_search}");
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
