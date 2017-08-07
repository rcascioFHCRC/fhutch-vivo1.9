<div id="wrapper-content" role="main">

    <section id="individual-intro" class="vcard" role="region" itemscope="" itemtype="http://schema.org/Organization">
        <section id="individual-info" role="region">
            <header>
                <h1>
                    <span class="fn">${title}</span><span class="display-title" style="padding-left: 10px; margin-left: 10px;">Leadership</span>
                </h1>
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

    <p>More information about our <a href="http://www.fredhutch.org/en/about/leadership.html">Leadership and Board</a></p>
    <p><a href="${urls.base}/org-browse">Browse Organizational Structure</a></p>

</div>
