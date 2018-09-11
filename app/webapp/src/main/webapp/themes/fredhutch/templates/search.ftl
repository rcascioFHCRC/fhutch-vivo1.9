<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#--Breaking this out so this can be utilized by other pages such as the jsp advanced tools pages-->
<div id="wrapper-search">
    <section id="search" role="region">
        <fieldset>
            <legend>${i18n().search_form}</legend>

            <form id="search-form" action="${urls.search}" name="search" role="search" accept-charset="UTF-8" method="GET">
                <div id="search-field">                    
                    <select name="classgroup">
                      <option value="">All</option>
                      <option value="http://vivoweb.org/ontology#vitroClassGrouppeople">People</option>
                      <option value="http://vivo.fredhutch.org/individual/vitroClassGrouppublications">Publications</option>
                      <option value="http://vivo.fredhutch.org/individual/vitroClassGroupexpertise">Expertise</option>
                    </select>
                    <input type="text" name="querytext" class="search-vivo" value="${querytext!}" autocapitalize="off" />
                    <input type="submit" value="${i18n().search_button}" class="search">
                </div>
            </form>
        </fieldset>
    </section>
</div>
