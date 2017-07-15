<div id="wrapper-content" role="main">

<section id="individual-intro" class="vcard" role="region" itemscope="" itemtype="http://schema.org/Organization">
    <section id="individual-info" role="region">
        <header>
            <h1 class="fn">${title} Leadership</h1>
            <h4><a class="website" href="http://www.fredhutch.org" title="website">Fred Hutch Website</a></h4>
        </header>
    </section>
</section>

<div id="person-browse">
    <#list people as person>
        <div class="overview">
            <div class="img-wrapper">
                <#if (person.picture)?hasContent>
                        <img class="thumbnail img-circle" src="${person.picture}"/>
                </#if>
            </div>
            <div class="details">
                <div class="name">
                    <a href="${profileUrl(person.p)}">${person.name}<#if (person.pTitle)?hasContent>, ${person.pTitle}</#if></a>
                </div>

                <div class="positions">
                    ${person.title}
                </div>
                <div class="clear"></div>
            </div>
        </div>
    </#list>
</div>

<hr/>
<div class="alpha-browse">
    <p>Browse all researchers by last name.</p>
    <ul>
        <#list alphabet as alpha>
            <li>
                <a href="${baseUrl}/${alpha}">${alpha?upperCase}</a>
            </li>
        </#list>
    </ul>
</div>


</div>
