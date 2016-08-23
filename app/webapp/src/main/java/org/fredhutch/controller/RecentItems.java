package org.fredhutch.controller;

import com.hp.hpl.jena.query.ParameterizedSparqlString;
import com.hp.hpl.jena.query.QuerySolution;
import com.hp.hpl.jena.rdf.model.Literal;
import com.hp.hpl.jena.rdf.model.Resource;
import edu.cornell.mannlib.vitro.webapp.controller.VitroRequest;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.UrlBuilder;
import edu.cornell.mannlib.vitro.webapp.rdfservice.RDFServiceException;
import edu.cornell.mannlib.vitro.webapp.rdfservice.ResultSetConsumer;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;


/**
 * Created by tedlawless on 8/23/16.
 */
public class RecentItems extends HttpServlet {

    private static final Log log = LogFactory.getLog(RecentItems.class.getName());


    protected final void doGet(HttpServletRequest req, HttpServletResponse response) throws ServletException, IOException {
        VitroRequest vreq = new VitroRequest(req);
        String path = vreq.getPathInfo();
        if (path != null) {
            String[] pathParts = path.split("/");
            log.debug("Recent items service: " + pathParts[1]);
            JSONArray items = new JSONArray();
            String requestType = pathParts[1];
            if (requestType.equals("news")) {
                items = getNewsItems(vreq);
            } else if (requestType.equals("pubs")){
                items = getPubItems(vreq);
            }
            response.setContentType("application/json");
            response.setCharacterEncoding("UTF-8");
            response.getWriter().write(items.toString());
        } else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }

    }

    public static JSONArray getNewsItems(VitroRequest vreq) {
        final JSONArray recent = new JSONArray();
        String rq = "" +
                "SELECT ?n ?title ?url ?date \n" +
                "WHERE { \n" +
                "   ?n a fhd:News ; \n" +
                "       rdfs:label ?title ; \n" +
                "       fhd:url ?url ; \n" +
                "       fhd:publishedOn ?date . \n" +
                "} \n" +
                "ORDER BY DESC(?date) \n" +
                "LIMIT 10\n";
        ParameterizedSparqlString q2 = new ParameterizedSparqlString();
        q2.setCommandText(rq);
        q2.setNsPrefix("fhd", "http://vivo.fredhutch.org/ontology/display#");
        q2.setNsPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
        q2.setNsPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
        String query = q2.toString();
        log.debug("Recent query:\n" + query);
        try {
            vreq.getRDFService().sparqlSelectQuery(query, new ResultSetConsumer() {
                @Override
                protected void processQuerySolution(QuerySolution qs) {
                    try {
                        recent.put(prepResult(qs));
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }

                }
            });
        } catch (RDFServiceException e) {
            e.printStackTrace();
        }
        return recent;
    }

    private static JSONObject prepResult(QuerySolution qs) throws JSONException {
        JSONObject item = new JSONObject();
        Literal name = qs.getLiteral("title");
        Resource uri = qs.getResource("n");
        Literal url = qs.getLiteral("url");
        Object date = qs.getLiteral("date").getValue();
        item.put("name", name);
        item.put("uri", uri);
        item.put("url", url);
        //thisArea.put("url", getURL(uri.toString(), vreq));
        item.put("date", date);
        return item;
    }

    public static JSONArray getPubItems(VitroRequest vreq) {
        final JSONArray recent = new JSONArray();
        String rq = "" +
                "SELECT ?n ?title ?url ?date \n" +
                "WHERE { \n" +
                "   ?n a fhp:Publication ; \n" +
                "       rdfs:label ?title ; \n" +
                "       vivo:dateTimeValue ?dt .\n" +
                "   ?dt vivo:dateTime ?date . \n" +
                "} \n" +
                "ORDER BY DESC(?date) \n" +
                "LIMIT 10\n";
        ParameterizedSparqlString q2 = new ParameterizedSparqlString();
        q2.setCommandText(rq);
        q2.setNsPrefix("fhd", "http://vivo.fredhutch.org/ontology/display#");
        q2.setNsPrefix("fhp", "http://vivo.fredhutch.org/ontology/publications#");
        q2.setNsPrefix("vivo", "http://vivoweb.org/ontology/core#");
        q2.setNsPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
        q2.setNsPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
        String query = q2.toString();
        log.debug("Recent query:\n" + query);
        try {
            vreq.getRDFService().sparqlSelectQuery(query, new ResultSetConsumer() {
                @Override
                protected void processQuerySolution(QuerySolution qs) {
                    JSONObject item = new JSONObject();
                    try {
                        Literal name = qs.getLiteral("title");
                        Resource uri = qs.getResource("n");
                        Object date = qs.getLiteral("date").getValue();
                        item.put("name", name);
                        item.put("uri", uri);
                        item.put("url", UrlBuilder.getHomeUrl() + "/individual?uri=" + uri);
                        item.put("date", date.toString().substring(0, 10));
                        recent.put(item);
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }

                }
            });
        } catch (RDFServiceException e) {
            e.printStackTrace();
        }
        return recent;
    }
}

