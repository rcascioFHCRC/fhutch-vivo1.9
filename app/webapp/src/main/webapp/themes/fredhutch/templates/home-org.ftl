<div id="wrapper-content" role="main">

<section id="individual-intro" class="vcard" role="region" itemscope="" itemtype="http://schema.org/Organization">
    <section id="individual-info" role="region">
        <header>
            <h1 class="fn">${title}</h1>
            <h4>Leadership</h4>
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

<p>More information about our <a href="http://www.fredhutch.org/en/about/leadership.html">Leadership and Board</a>
</p>
<p>
<a href="${urls.base}/org-browse">Browse Organizational Structure</a>
</p>

<div class="alpha-browse">
    <p>Browse all researchers by last name:</p>
    <ul>
        <#list alphabet as alpha>
            <li>
                <a href="${baseUrl}/${alpha}">${alpha?upperCase}</a>
            </li>
        </#list>
    </ul>
</div>

</div>
