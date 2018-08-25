package org.fredhutch.controller;

import com.google.common.base.Charsets;
import com.google.common.io.Resources;
import edu.cornell.mannlib.vitro.webapp.controller.VitroRequest;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.FreemarkerHttpServlet;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.UrlBuilder;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.ResponseValues;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.TemplateResponseValues;
import edu.cornell.mannlib.vitro.webapp.rdfservice.RDFServiceException;
import edu.cornell.mannlib.vitro.webapp.rdfservice.ResultSetConsumer;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.jena.query.ParameterizedSparqlString;
import org.apache.jena.query.QuerySolution;
import org.apache.jena.rdf.model.Literal;
import org.apache.jena.rdf.model.Resource;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
/**
 * Created by ted on 5/21/16.
 */
public class ExpertiseBrowseController extends FreemarkerHttpServlet {
    private static final Log log = LogFactory.getLog(ExpertiseBrowseController.class);
    private static final String TEMPLATE = "expertise-browse.ftl";
    private static final String QUERY = "expertiseBrowse/getAreas.rq";

    @Override
    protected ResponseValues processRequest(VitroRequest vreq) {
        log.debug("Generating expertise browse model");
        Map<String, Object> body = new HashMap<String, Object>();
        body.put("title", "Expertise");
        JSONArray areas = getAreas(vreq);
        body.put("areas", areas);
        return new TemplateResponseValues(TEMPLATE, body);
    }

    public static JSONArray getAreas(VitroRequest vreq) {
        //final ArrayList<HashMap> expertise = new ArrayList<HashMap>();
        final JSONArray expertise = new JSONArray();
        String rq = readQuery(QUERY);
        ParameterizedSparqlString q2 = new ParameterizedSparqlString();
        q2.setCommandText(rq);
        q2.setNsPrefix("foaf", "http://xmlns.com/foaf/0.1/");
        q2.setNsPrefix("vivo", "http://vivoweb.org/ontology/core#");
        q2.setNsPrefix("skos", "http://www.w3.org/2004/02/skos/core#");
        q2.setNsPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
        q2.setNsPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
        String query = q2.toString();
        log.debug("Expertise query:\n" + query);
        try {
            vreq.getRDFService().sparqlSelectQuery(query, new ResultSetConsumer() {
                @Override
                protected void processQuerySolution(QuerySolution qs) {
                    try {
                        expertise.put(prepResult(qs));
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }

                }
            });
        } catch (RDFServiceException e) {
            e.printStackTrace();
        }
        return expertise;
    }

    private static JSONObject prepResult(QuerySolution qs) throws JSONException {
        JSONObject thisArea = new JSONObject();
        Literal name = qs.getLiteral("label");
        Resource uri = qs.getResource("ex");
        Object number = qs.getLiteral("total").getValue();
        thisArea.put("name", name);
        thisArea.put("uri", uri);
        //thisArea.put("url", getURL(uri.toString(), vreq));
        thisArea.put("researchers", number);
        return thisArea;
    }

    public static String readQuery( String name ) {
        URL qurl = Resources.getResource(name);
        try {
            return Resources.toString(qurl, Charsets.UTF_8);
        } catch (IOException e) {
            e.printStackTrace();
            return "";
        }
    }

    public static String getURL( String uri, VitroRequest vreq ) {
        return UrlBuilder.getIndividualProfileUrl(uri, vreq);
    }
}
