//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by Fernflower decompiler)
//

package org.fredhutch.controller;

import edu.cornell.mannlib.vitro.webapp.application.ApplicationUtils;
import edu.cornell.mannlib.vitro.webapp.beans.ApplicationBean;
import edu.cornell.mannlib.vitro.webapp.beans.Individual;
import edu.cornell.mannlib.vitro.webapp.beans.VClass;
import edu.cornell.mannlib.vitro.webapp.beans.VClassGroup;
import edu.cornell.mannlib.vitro.webapp.config.ConfigurationProperties;
import edu.cornell.mannlib.vitro.webapp.controller.VitroRequest;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.FreemarkerHttpServlet;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.UrlBuilder;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.UrlBuilder.ParamMap;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.ExceptionResponseValues;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.ResponseValues;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.TemplateResponseValues;
import edu.cornell.mannlib.vitro.webapp.dao.IndividualDao;
import edu.cornell.mannlib.vitro.webapp.dao.VClassDao;
import edu.cornell.mannlib.vitro.webapp.dao.VClassGroupDao;
import edu.cornell.mannlib.vitro.webapp.dao.VClassGroupsForRequest;
import edu.cornell.mannlib.vitro.webapp.dao.jena.VClassGroupCache;
import edu.cornell.mannlib.vitro.webapp.i18n.I18n;
import edu.cornell.mannlib.vitro.webapp.modules.searchEngine.SearchEngine;
import edu.cornell.mannlib.vitro.webapp.modules.searchEngine.SearchFacetField;
import edu.cornell.mannlib.vitro.webapp.modules.searchEngine.SearchQuery;
import edu.cornell.mannlib.vitro.webapp.modules.searchEngine.SearchResponse;
import edu.cornell.mannlib.vitro.webapp.modules.searchEngine.SearchResultDocument;
import edu.cornell.mannlib.vitro.webapp.modules.searchEngine.SearchResultDocumentList;
import edu.cornell.mannlib.vitro.webapp.modules.searchEngine.SearchFacetField.Count;
import edu.cornell.mannlib.vitro.webapp.web.templatemodels.LinkTemplateModel;
import edu.cornell.mannlib.vitro.webapp.web.templatemodels.searchresult.IndividualSearchResult;
import edu.ucsf.vitro.opensocial.OpenSocialManager;
import java.io.IOException;
import java.sql.SQLException;
import java.util.*;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.apache.commons.lang.StringUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

public class FredHutchPagedSearchController extends FreemarkerHttpServlet {
    private static final long serialVersionUID = 1L;
    private static final Log log = LogFactory.getLog(FredHutchPagedSearchController.class);
    protected static final int DEFAULT_HITS_PER_PAGE = 25;
    protected static final int DEFAULT_MAX_HIT_COUNT = 1000;
    private static final String PARAM_XML_REQUEST = "xml";
    private static final String PARAM_CSV_REQUEST = "csv";
    private static final String PARAM_START_INDEX = "startIndex";
    private static final String PARAM_HITS_PER_PAGE = "hitsPerPage";
    private static final String PARAM_CLASSGROUP = "classgroup";
    private static final String PARAM_RDFTYPE = "type";
    private static final String PARAM_QUERY_TEXT = "querytext";
    protected static final Map<FredHutchPagedSearchController.Format, Map<FredHutchPagedSearchController.Result, String>> templateTable = setupTemplateTable();
    public static final int MAX_QUERY_LENGTH = 500;
    public static final ArrayList<String> FACET_EXCLUDE = new ArrayList<String>() {{
        add("http://vivo.fredhutch.org/ontology/publications#Publication");
        add("http://vivo.fredhutch.org/ontology/display#HutchNews");
        add("http://www.w3.org/2004/02/skos/core#Concept");
        add("http://xmlns.com/foaf/0.1/Organization");
        add("http://vivo.fredhutch.org/ontology/display#InternalOrganization");
        add("http://vivo.fredhutch.org/ontology/clinicaltrials#ClinicalTrial");
    }};

    public FredHutchPagedSearchController() {
    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException, ServletException {
        VitroRequest vreq = new VitroRequest(request);
        boolean wasXmlRequested = this.isRequestedFormatXml(vreq);
        boolean wasCSVRequested = this.isRequestedFormatCSV(vreq);
        if(!wasXmlRequested && !wasCSVRequested) {
            super.doGet(vreq, response);
        } else {
            ResponseValues e;
            if(wasXmlRequested) {
                try {
                    e = this.processRequest(vreq);
                    response.setCharacterEncoding("UTF-8");
                    response.setContentType("text/xml;charset=UTF-8");
                    response.setHeader("Content-Disposition", "attachment; filename=search.xml");
                    this.writeTemplate(e.getTemplateName(), e.getMap(), request, response);
                } catch (Exception var8) {
                    log.error(var8, var8);
                }
            } else if(wasCSVRequested) {
                try {
                    e = this.processRequest(vreq);
                    response.setCharacterEncoding("UTF-8");
                    response.setContentType("text/csv;charset=UTF-8");
                    response.setHeader("Content-Disposition", "attachment; filename=search.csv");
                    this.writeTemplate(e.getTemplateName(), e.getMap(), request, response);
                } catch (Exception var7) {
                    log.error(var7, var7);
                }
            }
        }

    }

    protected ResponseValues processRequest(VitroRequest vreq) {
        FredHutchPagedSearchController.Format format = this.getFormat(vreq);
        boolean wasXmlRequested = FredHutchPagedSearchController.Format.XML == format;
        boolean wasCSVRequested = FredHutchPagedSearchController.Format.CSV == format;
        log.debug("Requested format was " + (wasXmlRequested?"xml":"html"));
        boolean wasHtmlRequested = !wasXmlRequested && !wasCSVRequested;

        try {
            if(vreq.getWebappDaoFactory() != null && vreq.getWebappDaoFactory().getIndividualDao() != null) {
                IndividualDao e = vreq.getWebappDaoFactory().getIndividualDao();
                VClassGroupDao grpDao = vreq.getWebappDaoFactory().getVClassGroupDao();
                VClassDao vclassDao = vreq.getWebappDaoFactory().getVClassDao();
                ApplicationBean appBean = vreq.getAppBean();
                log.debug("IndividualDao is " + e.toString() + " Public classes in the classgroup are " + grpDao.getPublicGroupsWithVClasses().toString());
                log.debug("VClassDao is " + vclassDao.toString());
                int startIndex = this.getStartIndex(vreq);
                int hitsPerPage = this.getHitsPerPage(vreq);
                String queryText = vreq.getParameter("querytext");
                log.debug("Query text is \"" + queryText + "\"");
                String badQueryMsg = this.badQueryText(queryText, vreq);
                if(badQueryMsg != null) {
                    return this.doFailedSearch(badQueryMsg, queryText, format, vreq);
                } else {
                    SearchQuery query = this.getQuery(queryText, hitsPerPage, startIndex, vreq);
                    SearchEngine search = ApplicationUtils.instance().getSearchEngine();
                    SearchResponse response = null;

                    try {
                        response = search.query(query);
                    } catch (Exception var33) {
                        String hitCount = this.makeBadSearchMessage(queryText, var33.getMessage(), vreq);
                        log.error("could not run search query", var33);
                        return this.doFailedSearch(hitCount, queryText, format, vreq);
                    }

                    if(response == null) {
                        log.error("Search response was null");
                        return this.doFailedSearch(I18n.text(vreq, "error_in_search_request", new Object[0]), queryText, format, vreq);
                    } else {
                        SearchResultDocumentList docs = response.getResults();
                        if(docs == null) {
                            log.error("Document list for a search was null");
                            return this.doFailedSearch(I18n.text(vreq, "error_in_search_request", new Object[0]), queryText, format, vreq);
                        } else {
                            long hitCount1 = docs.getNumFound();
                            log.debug("Number of hits = " + hitCount1);
                            if(hitCount1 < 1L) {
                                return this.doNoHits(queryText, format, vreq);
                            } else {
                                ArrayList individuals = new ArrayList(docs.size());
                                Iterator docIter = docs.iterator();

                                while(docIter.hasNext()) {
                                    try {
                                        SearchResultDocument pagingLinkParams = (SearchResultDocument)docIter.next();
                                        String body = pagingLinkParams.getStringValue("URI");
                                        Individual classGroupParam = e.getIndividualByURI(body);
                                        if(classGroupParam != null) {
                                            classGroupParam.setSearchSnippet(this.getSnippet(pagingLinkParams, response));
                                            individuals.add(classGroupParam);
                                        }
                                    } catch (Exception var32) {
                                        log.error("Problem getting usable individuals from search hits. ", var32);
                                    }
                                }

                                ParamMap pagingLinkParams1 = new ParamMap();
                                pagingLinkParams1.put("querytext", queryText);
                                pagingLinkParams1.put("hitsPerPage", String.valueOf(hitsPerPage));
                                if(wasXmlRequested) {
                                    pagingLinkParams1.put("xml", "1");
                                }

                                HashMap body1 = new HashMap();
                                String classGroupParam1 = vreq.getParameter("classgroup");
                                log.debug("ClassGroupParam is \"" + classGroupParam1 + "\"");
                                boolean classGroupFilterRequested = false;
                                if(!StringUtils.isEmpty(classGroupParam1)) {
                                    VClassGroup typeParam = grpDao.getGroupByURI(classGroupParam1);
                                    classGroupFilterRequested = true;
                                    if(typeParam != null && typeParam.getPublicName() != null) {
                                        body1.put("classGroupName", typeParam.getPublicName());
                                    }
                                }

                                String typeParam1 = vreq.getParameter("type");
                                boolean typeFilterRequested = false;
                                if(!StringUtils.isEmpty(typeParam1)) {
                                    VClass template = vclassDao.getVClassByURI(typeParam1);
                                    typeFilterRequested = true;
                                    if(template != null && template.getName() != null) {
                                        body1.put("typeName", template.getName());
                                    }
                                }

                                if(wasHtmlRequested) {
                                    if(!classGroupFilterRequested && !typeFilterRequested) {
                                        body1.put("classGroupLinks", this.getClassGroupsLinks(vreq, grpDao, docs, response, queryText));
                                    } else if(classGroupFilterRequested && !typeFilterRequested) {
                                        body1.put("classLinks", this.getVClassLinks(vclassDao, docs, response, queryText));
                                        pagingLinkParams1.put("classgroup", classGroupParam1);
                                    } else {
                                        pagingLinkParams1.put("type", typeParam1);
                                    }
                                }

                                body1.put("individuals", IndividualSearchResult.getIndividualTemplateModels(individuals, vreq));
                                body1.put("querytext", queryText);
                                body1.put("title", queryText + " - " + appBean.getApplicationName() + " Search Results");
                                body1.put("hitCount", Long.valueOf(hitCount1));
                                body1.put("startIndex", Integer.valueOf(startIndex));
                                body1.put("pagingLinks", getPagingLinks(startIndex, hitsPerPage, hitCount1, vreq.getServletPath(), pagingLinkParams1, vreq));
                                if(startIndex != 0) {
                                    body1.put("prevPage", this.getPreviousPageLink(startIndex, hitsPerPage, vreq.getServletPath(), pagingLinkParams1));
                                }

                                if((long)startIndex < hitCount1 - (long)hitsPerPage) {
                                    body1.put("nextPage", this.getNextPageLink(startIndex, hitsPerPage, vreq.getServletPath(), pagingLinkParams1));
                                }

                                try {
                                    OpenSocialManager template1 = new OpenSocialManager(vreq, "search");
                                    if("http://vivoweb.org/ontology#vitroClassGrouppeople".equals(vreq.getParameter("classgroup"))) {
                                        List ids = OpenSocialManager.getOpenSocialId(individuals);
                                        template1.setPubsubData("JSONPersonIds", OpenSocialManager.buildJSONPersonIds(ids, "" + ids.size() + " people found"));
                                    }

                                    template1.removePubsubGadgetsWithoutData();
                                    body1.put("openSocial", template1);
                                    if(template1.isVisible()) {
                                        body1.put("bodyOnload", "my.init();");
                                    }
                                } catch (IOException var30) {
                                    log.error("IOException in doTemplate()", var30);
                                } catch (SQLException var31) {
                                    log.error("SQLException in doTemplate()", var31);
                                }

                                String template2 = (String)((Map)templateTable.get(format)).get(FredHutchPagedSearchController.Result.PAGED);
                                return new TemplateResponseValues(template2, body1);
                            }
                        }
                    }
                }
            } else {
                log.error("Could not get webappDaoFactory or IndividualDao");
                throw new Exception("Could not access model.");
            }
        } catch (Throwable var34) {
            return this.doSearchError(var34, format);
        }
    }

    private int getHitsPerPage(VitroRequest vreq) {
        boolean hitsPerPage = true;

        int hitsPerPage1;
        try {
            hitsPerPage1 = Integer.parseInt(vreq.getParameter("hitsPerPage"));
        } catch (Throwable var4) {
            hitsPerPage1 = 25;
        }

        log.debug("hitsPerPage is " + hitsPerPage1);
        return hitsPerPage1;
    }

    private int getStartIndex(VitroRequest vreq) {
        boolean startIndex = false;

        int startIndex1;
        try {
            startIndex1 = Integer.parseInt(vreq.getParameter("startIndex"));
        } catch (Throwable var4) {
            startIndex1 = 0;
        }

        log.debug("startIndex is " + startIndex1);
        return startIndex1;
    }

    private String badQueryText(String qtxt, VitroRequest vreq) {
        return qtxt != null && !"".equals(qtxt.trim())?(qtxt.equals("*:*")?I18n.text(vreq, "invalid_search_term", new Object[0]):null):I18n.text(vreq, "enter_search_term", new Object[0]);
    }

    private List<FredHutchPagedSearchController.VClassGroupSearchLink> getClassGroupsLinks(VitroRequest vreq, VClassGroupDao grpDao, SearchResultDocumentList docs, SearchResponse rsp, String qtxt) {
        HashMap cgURItoCount = new HashMap();
        ArrayList classgroups = new ArrayList();
        List ffs = rsp.getFacetFields();
        Iterator vcgfr = ffs.iterator();

        while(true) {
            SearchFacetField classGroupLinks;
            VClassGroup localizedVcg;
            do {
                if(!vcgfr.hasNext()) {
                    grpDao.sortGroupList(classgroups);
                    VClassGroupsForRequest vcgfr1 = VClassGroupCache.getVClassGroups(vreq);
                    ArrayList classGroupLinks1 = new ArrayList(classgroups.size());
                    Iterator counts1 = classgroups.iterator();

                    while(counts1.hasNext()) {
                        VClassGroup vcg1 = (VClassGroup)counts1.next();
                        String groupURI1 = vcg1.getURI();
                        localizedVcg = vcgfr1.getGroup(groupURI1);
                        long count = ((Long)cgURItoCount.get(groupURI1)).longValue();
                        if(localizedVcg.getPublicName() != null && count > 0L) {
                            classGroupLinks1.add(new FredHutchPagedSearchController.VClassGroupSearchLink(qtxt, localizedVcg, count));
                        }
                    }

                    return classGroupLinks1;
                }

                classGroupLinks = (SearchFacetField)vcgfr.next();
            } while(!"classgroup".equals(classGroupLinks.getName()));

            List counts = classGroupLinks.getValues();
            Iterator vcg = counts.iterator();

            while(vcg.hasNext()) {
                Count groupURI = (Count)vcg.next();
                localizedVcg = grpDao.getGroupByURI(groupURI.getName());
                if(localizedVcg == null) {
                    log.debug("could not get classgroup for URI " + groupURI.getName());
                } else {
                    classgroups.add(localizedVcg);
                    cgURItoCount.put(localizedVcg.getURI(), Long.valueOf(groupURI.getCount()));
                }
            }
        }
    }

    private List<FredHutchPagedSearchController.VClassSearchLink> getVClassLinks(VClassDao vclassDao, SearchResultDocumentList docs, SearchResponse rsp, String qtxt) {
        HashSet typesInHits = this.getVClassUrisForHits(docs);
        ArrayList classes = new ArrayList(typesInHits.size());
        HashMap typeURItoCount = new HashMap();
        List ffs = rsp.getFacetFields();
        Iterator vClassLinks = ffs.iterator();

        while(true) {
            SearchFacetField ff;
            do {
                if(!vClassLinks.hasNext()) {
                    classes.sort(Comparator.comparing(VClass::getName));
                    ArrayList vClassLinks1 = new ArrayList(classes.size());
                    Iterator ff1 = classes.iterator();

                    while(ff1.hasNext()) {
                        VClass vc1 = (VClass)ff1.next();
                        long count2 = ((Long)typeURItoCount.get(vc1.getURI())).longValue();
                        vClassLinks1.add(new FredHutchPagedSearchController.VClassSearchLink(qtxt, vc1, count2));
                    }

                    return vClassLinks1;
                }

                ff = (SearchFacetField)vClassLinks.next();
            } while(!"type".equals(ff.getName()));

            List vc = ff.getValues();
            Iterator count = vc.iterator();

            while(count.hasNext()) {
                Count ct = (Count)count.next();
                String typeUri = ct.getName();
                long count1 = ct.getCount();

                try {
                    if(!"http://www.w3.org/2002/07/owl#Thing".equals(typeUri) && count1 != 0L) {
                        VClass ex = vclassDao.getVClassByURI(typeUri);
                        if(ex != null && !ex.isAnonymous() && ex.getName() != null && !"".equals(ex.getName()) && ex.getGroupURI() != null) {
                            if(!FACET_EXCLUDE.contains(typeUri)) {
                                typeURItoCount.put(typeUri, Long.valueOf(count1));
                                classes.add(ex);
                            }
                        }
                    }
                } catch (Exception var18) {
                    if(log.isDebugEnabled()) {
                        log.debug("could not add type " + typeUri, var18);
                    }
                }
            }
        }
    }

    private HashSet<String> getVClassUrisForHits(SearchResultDocumentList docs) {
        HashSet typesInHits = new HashSet();
        Iterator var3 = docs.iterator();

        while(var3.hasNext()) {
            SearchResultDocument doc = (SearchResultDocument)var3.next();

            try {
                Collection e = doc.getFieldValues("type");
                if(e != null) {
                    Iterator var6 = e.iterator();

                    while(var6.hasNext()) {
                        Object o = var6.next();
                        String typeUri = o.toString();
                        typesInHits.add(typeUri);
                    }
                }
            } catch (Exception var9) {
                log.error("problems getting rdf:type for search hits", var9);
            }
        }

        return typesInHits;
    }

    private String getSnippet(SearchResultDocument doc, SearchResponse response) {
        String docId = doc.getStringValue("DocId");
        StringBuffer text = new StringBuffer();
        Map highlights = response.getHighlighting();
        if(highlights != null && highlights.get(docId) != null) {
            List snippets = (List)((Map)highlights.get(docId)).get("ALLTEXT");
            if(snippets != null && snippets.size() > 0) {
                text.append("... " + (String)snippets.get(0) + " ...");
            }
        }

        return text.toString();
    }

    private SearchQuery getQuery(String queryText, int hitsPerPage, int startIndex, VitroRequest vreq) {
        SearchQuery query = ApplicationUtils.instance().getSearchEngine().createQuery(queryText);
        query.setStart(startIndex).setRows(hitsPerPage);
        String classgroupParam = vreq.getParameter("classgroup");
        String typeParam = vreq.getParameter("type");
        if(!StringUtils.isBlank(classgroupParam)) {
            log.debug("Firing classgroup query ");
            log.debug("request.getParameter(classgroup) is " + classgroupParam);
            query.addFilterQuery("classgroup:\"" + classgroupParam + "\"");
            query.addFacetFields(new String[]{"type"}).setFacetLimit(-1);
        } else if(!StringUtils.isBlank(typeParam)) {
            log.debug("Firing type query ");
            log.debug("request.getParameter(type) is " + typeParam);
            query.addFilterQuery("type:\"" + typeParam + "\"");
        } else {
            query.addFacetFields(new String[]{"classgroup"}).setFacetLimit(-1);
        }

        log.debug("Query = " + query.toString());
        return query;
    }

    protected static List<FredHutchPagedSearchController.PagingLink> getPagingLinks(int startIndex, int hitsPerPage, long hitCount, String baseUrl, ParamMap params, VitroRequest vreq) {
        ArrayList pagingLinks = new ArrayList();
        if(hitCount <= (long)hitsPerPage) {
            return pagingLinks;
        } else {
            int maxHitCount = 1000;
            if(startIndex >= 1000 - hitsPerPage) {
                maxHitCount = startIndex + 1000;
            }

            for(int i = 0; (long)i < hitCount; i += hitsPerPage) {
                params.put("startIndex", String.valueOf(i));
                if(i >= maxHitCount - hitsPerPage) {
                    pagingLinks.add(new FredHutchPagedSearchController.PagingLink(I18n.text(vreq, "paging_link_more", new Object[0]), baseUrl, params));
                    break;
                }

                int pageNumber = i / hitsPerPage + 1;
                boolean iIsCurrentPage = i >= startIndex && i < startIndex + hitsPerPage;
                if(iIsCurrentPage) {
                    pagingLinks.add(new FredHutchPagedSearchController.PagingLink(pageNumber));
                } else {
                    pagingLinks.add(new FredHutchPagedSearchController.PagingLink(pageNumber, baseUrl, params));
                }
            }

            return pagingLinks;
        }
    }

    private String getPreviousPageLink(int startIndex, int hitsPerPage, String baseUrl, ParamMap params) {
        params.put("startIndex", String.valueOf(startIndex - hitsPerPage));
        return UrlBuilder.getUrl(baseUrl, params);
    }

    private String getNextPageLink(int startIndex, int hitsPerPage, String baseUrl, ParamMap params) {
        params.put("startIndex", String.valueOf(startIndex + hitsPerPage));
        return UrlBuilder.getUrl(baseUrl, params);
    }

    private ExceptionResponseValues doSearchError(Throwable e, FredHutchPagedSearchController.Format f) {
        HashMap body = new HashMap();
        body.put("message", "Search failed: " + e.getMessage());
        return new ExceptionResponseValues(getTemplate(f, FredHutchPagedSearchController.Result.ERROR), body, e);
    }

    private TemplateResponseValues doFailedSearch(String message, String querytext, FredHutchPagedSearchController.Format f, VitroRequest vreq) {
        HashMap body = new HashMap();
        body.put("title", I18n.text(vreq, "search_for", new Object[]{querytext}));
        if(StringUtils.isEmpty(message)) {
            message = I18n.text(vreq, "search_failed", new Object[0]);
        }

        body.put("message", message);
        return new TemplateResponseValues(getTemplate(f, FredHutchPagedSearchController.Result.ERROR), body);
    }

    private TemplateResponseValues doNoHits(String querytext, FredHutchPagedSearchController.Format f, VitroRequest vreq) {
        HashMap body = new HashMap();
        body.put("title", I18n.text(vreq, "search_for", new Object[]{querytext}));
        body.put("message", I18n.text(vreq, "no_matching_results", new Object[0]));
        return new TemplateResponseValues(getTemplate(f, FredHutchPagedSearchController.Result.ERROR), body);
    }

    private String makeBadSearchMessage(String querytext, String exceptionMsg, VitroRequest vreq) {
        String rv = "";

        try {
            int ex = exceptionMsg.indexOf("column");
            if(ex == -1) {
                return "";
            } else {
                int numi = exceptionMsg.indexOf(".", ex + 7);
                if(numi == -1) {
                    return "";
                } else {
                    String part = exceptionMsg.substring(ex + 7, numi);
                    int i = Integer.parseInt(part) - 1;
                    byte errorWindow = 5;
                    int pre = i - errorWindow;
                    if(pre < 0) {
                        pre = 0;
                    }

                    int post = i + errorWindow;
                    if(post > querytext.length()) {
                        post = querytext.length();
                    }

                    String before = querytext.substring(pre, i);
                    String after = "";
                    if(post > i) {
                        after = querytext.substring(i + 1, post);
                    }

                    rv = I18n.text(vreq, "search_term_error_near", new Object[0]) + " <span class=\'searchQuote\'>" + before + "<span class=\'searchError\'>" + querytext.charAt(i) + "</span>" + after + "</span>";
                    return rv;
                }
            }
        } catch (Throwable var14) {
            return "";
        }
    }

    protected boolean isRequestedFormatXml(VitroRequest req) {
        if(req != null) {
            String param = req.getParameter("xml");
            return param != null && "1".equals(param);
        } else {
            return false;
        }
    }

    protected boolean isRequestedFormatCSV(VitroRequest req) {
        if(req != null) {
            String param = req.getParameter("csv");
            return param != null && "1".equals(param);
        } else {
            return false;
        }
    }

    protected FredHutchPagedSearchController.Format getFormat(VitroRequest req) {
        return req != null && req.getParameter("xml") != null && "1".equals(req.getParameter("xml"))? FredHutchPagedSearchController.Format.XML:(req != null && req.getParameter("csv") != null && "1".equals(req.getParameter("csv"))? FredHutchPagedSearchController.Format.CSV: FredHutchPagedSearchController.Format.HTML);
    }

    protected static String getTemplate(FredHutchPagedSearchController.Format format, FredHutchPagedSearchController.Result result) {
        if(format != null && result != null) {
            return (String)((Map)templateTable.get(format)).get(result);
        } else {
            log.error("getTemplate() must not have a null format or result.");
            return (String)((Map)templateTable.get(FredHutchPagedSearchController.Format.HTML)).get(FredHutchPagedSearchController.Result.ERROR);
        }
    }

    protected static Map<FredHutchPagedSearchController.Format, Map<FredHutchPagedSearchController.Result, String>> setupTemplateTable() {
        HashMap table = new HashMap();
        HashMap resultsToTemplates = new HashMap();
        resultsToTemplates.put(FredHutchPagedSearchController.Result.PAGED, "search-pagedResults.ftl");
        resultsToTemplates.put(FredHutchPagedSearchController.Result.ERROR, "search-error.ftl");
        table.put(FredHutchPagedSearchController.Format.HTML, Collections.unmodifiableMap(resultsToTemplates));
        resultsToTemplates = new HashMap();
        resultsToTemplates.put(FredHutchPagedSearchController.Result.PAGED, "search-xmlResults.ftl");
        resultsToTemplates.put(FredHutchPagedSearchController.Result.ERROR, "search-xmlError.ftl");
        table.put(FredHutchPagedSearchController.Format.XML, Collections.unmodifiableMap(resultsToTemplates));
        resultsToTemplates = new HashMap();
        resultsToTemplates.put(FredHutchPagedSearchController.Result.PAGED, "search-csvResults.ftl");
        resultsToTemplates.put(FredHutchPagedSearchController.Result.ERROR, "search-csvError.ftl");
        table.put(FredHutchPagedSearchController.Format.CSV, Collections.unmodifiableMap(resultsToTemplates));
        return Collections.unmodifiableMap(table);
    }

    protected static class PagingLink extends LinkTemplateModel {
        PagingLink(int pageNumber, String baseUrl, ParamMap params) {
            super(String.valueOf(pageNumber), baseUrl, params);
        }

        PagingLink(int pageNumber) {
            this.setText(String.valueOf(pageNumber));
        }

        PagingLink(String text, String baseUrl, ParamMap params) {
            super(text, baseUrl, params);
        }
    }

    public static class VClassSearchLink extends LinkTemplateModel {
        long count = 0L;

        VClassSearchLink(String querytext, VClass type, long count) {
            super(type.getName(), "/search", new String[]{"querytext", querytext, "type", type.getURI()});
            this.count = count;
        }

        public String getCount() {
            return Long.toString(this.count);
        }
    }

    public static class VClassGroupSearchLink extends LinkTemplateModel {
        long count = 0L;

        VClassGroupSearchLink(String querytext, VClassGroup classgroup, long count) {
            super(classgroup.getPublicName(), "/search", new String[]{"querytext", querytext, "classgroup", classgroup.getURI()});
            this.count = count;
        }

        public String getCount() {
            return Long.toString(this.count);
        }
    }

    protected static enum Result {
        PAGED,
        ERROR,
        BAD_QUERY;

        private Result() {
        }
    }

    protected static enum Format {
        HTML,
        XML,
        CSV;

        private Format() {
        }
    }
}
