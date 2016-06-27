<#-- $This file is distributed under the terms of the license in /doc/license.txt$ -->

<#--Breaking this out so this can be utilized by other pages such as the jsp advanced tools pages-->

<section id="search" role="region">
    <fieldset>
        <legend>${i18n().search_form}</legend>

        <form id="search-form" action="${urls.search}" name="search" role="search" accept-charset="UTF-8" method="POST">
            <div id="search-field">
                <input type="text" name="querytext" class="search-vivo" value="${querytext!}" autocapitalize="off" />
                <select name="classgroup">
                  <option value="">All</option>
                  <option value="http://vivoweb.org/ontology#vitroClassGrouppeople">People</option>
                  <option value="http://vivoweb.org/ontology#vitroClassGrouporganizations">Organizations</option>
                  <option value="http://vivo.fredhutch.org/individual/vitroClassGrouppublications">Publications</option>
                  <option value="http://vivo.fredhutch.org/individual/vitroClassGroupexpertise">Expertise</option>
                  <option value="http://vivo.fredhutch.org/individual/vitroClassGroupclinicaltrials">Clinical trials</option>
                  <option value="http://vivo.fredhutch.org/individual/vitroClassGroupNews">News
                  </option>
                </select>
                <input type="submit" value="${i18n().search_button}" class="search">
            </div>
        </form>
    </fieldset>
</section>

