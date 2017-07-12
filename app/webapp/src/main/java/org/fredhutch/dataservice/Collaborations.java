package org.fredhutch.dataservice;

import com.hp.hpl.jena.query.ParameterizedSparqlString;
import com.hp.hpl.jena.query.QuerySolution;
import com.hp.hpl.jena.rdf.model.Literal;
import com.hp.hpl.jena.rdf.model.Resource;
import edu.cornell.mannlib.vitro.webapp.config.ConfigurationProperties;
import edu.cornell.mannlib.vitro.webapp.controller.VitroHttpServlet;
import edu.cornell.mannlib.vitro.webapp.controller.VitroRequest;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.UrlBuilder;
import edu.cornell.mannlib.vitro.webapp.rdfservice.RDFServiceException;
import edu.cornell.mannlib.vitro.webapp.rdfservice.ResultSetConsumer;
import edu.cornell.mannlib.vitro.webapp.visualization.coauthorship.CoAuthorshipQueryRunner;
import edu.cornell.mannlib.vitro.webapp.visualization.collaborationutils.CoAuthorshipData;
import edu.cornell.mannlib.vitro.webapp.visualization.valueobjects.Collaborator;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.fredhutch.utils.StoreUtils;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.*;



public class Collaborations extends VitroHttpServlet {

    private static final Log log = LogFactory.getLog(Collaborations.class.getName());
    private String namespace;
    private StoreUtils storeUtils;



    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException, ServletException {
        ConfigurationProperties props = ConfigurationProperties.getBean(request);
        namespace = props.getProperty("Vitro.defaultNamespace");

        VitroRequest vreq = new VitroRequest(request);
        String path = vreq.getPathInfo();

        //setup storeUtils
        this.storeUtils = new StoreUtils();
        this.storeUtils.setRdfService(namespace, vreq.getRDFService());

        String[] pathParts = path.split("/");
        String ln = pathParts[1];
        String uri = namespace + ln;
        HashMap oinfo = getOrgInfo(uri, vreq);
        ArrayList members = getOrgMembers(uri, vreq);
        JSONObject coauthors = getCoauthors(vreq, members);
        JSONObject exit = new JSONObject();
        try {
            exit.put("details", oinfo);
            exit.put("edges", coauthors.get("connections"));
            exit.put("nodes", coauthors.get("collab"));
        } catch (JSONException e) {
            e.printStackTrace();
        }
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        response.getWriter().write(exit.toString());

    }

    private JSONObject getCoauthors(VitroRequest vreq, ArrayList researcherGroup) {
        String thisName;
        String thisLocalName;
        String thisURI;
        ArrayList items = new ArrayList();
        ArrayList done = new ArrayList();
        ArrayList meta = new ArrayList();
        for (Object thisMember : researcherGroup) {
            log.debug("processing: " + thisMember);
            //String egoURI = namespace + localName;
            CoAuthorshipQueryRunner queryManager = new CoAuthorshipQueryRunner(thisMember.toString(), vreq, log);
            try {
                CoAuthorshipData authorNodesAndEdges = queryManager.getQueryResult();
                Iterator var3 = authorNodesAndEdges.getCollaborators().iterator();

                Collaborator thisCollab = authorNodesAndEdges.getEgoCollaborator();
                thisName = thisCollab.getCollaboratorName();
                thisURI = thisCollab.getCollaboratorURI();
                thisLocalName = thisURI.replace(namespace, "");
                Integer totalCollabs = 0;
                // person info
                JSONObject thisMeta = new JSONObject();
                try {
                    thisMeta.put("name", thisName);
                    thisMeta.put("uri", thisURI);
                    thisMeta.put("id", thisLocalName);
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                while(var3.hasNext()) {
                    JSONObject item = new JSONObject();
                    Collaborator currNode = (Collaborator)var3.next();
                    String collabURI = currNode.getCollaboratorURI();
                    String collabLocalName = collabURI.replace(namespace, "");
                    // if this researcher is in this group
                    if(currNode != authorNodesAndEdges.getEgoCollaborator())
                        if (researcherGroup.contains(collabURI)) {
                            String doneKey = makeDoneKey(thisLocalName, collabLocalName);
                            // increment total collab count outside of done check
                            totalCollabs += 1;
                            if (!done.contains(doneKey)) {
                                int strength = currNode.getNumOfActivities();
                                try {
                                    item.put("source", thisLocalName);
                                    item.put("target", collabLocalName);
                                    item.put("strength", strength);
                                } catch (JSONException e) {
                                    e.printStackTrace();
                                }
                                items.add(item);
                                done.add(doneKey);
                            }
                        }
                }
                //add total collabs
                thisMeta.put("total", totalCollabs);
                meta.add(thisMeta);
            } catch (Exception e) {
                //e.printStackTrace();
                log.error("Error processing:  " + thisMember);
            }

        }
        JSONObject out = new JSONObject();
        try {
            out.put("collab", new JSONArray(meta));
            out.put("connections", new JSONArray(items));
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return out;
    }

    private String makeDoneKey(String a, String b) {
        //Create a key for each collaboration so that we don't duplicate
        //the results.
        //http://stackoverflow.com/a/605901/758157
        String key = a + b;
        char[] chars = key.toCharArray();
        Arrays.sort(chars);
        String sorted = new String(chars);
        return sorted;
    }

    /*  org info */
    @SuppressWarnings("unchecked")
    private static HashMap getOrgInfo(final String orgUri, VitroRequest vreq) {
        log.debug("Running org query");
        final HashMap info = new HashMap();
        String rq = "" +
                "SELECT ?name ?overview \n" +
                "WHERE { \n" +
                "   ?org a foaf:Organization ; \n" +
                "       rdfs:label ?name . \n" +
                "OPTIONAL { ?org vivo:overview ?overview } \n" +
                "}";
        ParameterizedSparqlString q2 = new ParameterizedSparqlString();
        q2.setCommandText(rq);
        q2.setIri("org", orgUri);
        q2.setNsPrefix("foaf", "http://xmlns.com/foaf/0.1/");
        q2.setNsPrefix("vivo", "http://vivoweb.org/ontology/core#");
        q2.setNsPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
        q2.setNsPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
        String query = q2.toString();
        log.debug("Recent query:\n" + query);
        try {
            vreq.getRDFService().sparqlSelectQuery(query, new ResultSetConsumer() {
                @Override
                protected void processQuerySolution(QuerySolution qs) {

                    Literal name = qs.getLiteral("name");
                    Literal overview = qs.getLiteral("overview");
                    info.put("name", name);
                    info.put("uri", orgUri);
                    info.put("url", UrlBuilder.getHomeUrl() + "/individual?uri=" + orgUri);
                    info.put("overview", overview);

                }
            });
        } catch (RDFServiceException e) {
            e.printStackTrace();
        }
        return info;
    }

    @SuppressWarnings("unchecked")
    private ArrayList getOrgMembers(String orgUri, VitroRequest vreq) {
        log.debug("Running org query");
        final ArrayList members = new ArrayList<String>();
        String rq = "" +
                "SELECT DISTINCT ?person \n" +
                "WHERE { \n" +
                "{" +
                "?org a foaf:Organization ; \n" +
                "       vivo:relatedBy ?pos . \n" +
                "?pos a vivo:Position ; \n" +
                "       vivo:relates ?org, ?person .\n" +
                "?person a foaf:Person ." +
                "}" +
                "UNION {" +
                "?org a foaf:Organization ; \n" +
                "      obo:BFO_0000051 ?childOrg .\n" +
                "?childOrg a foaf:Organization ; \n"+
                "   vivo:relatedBy ?pos . \n" +
                "?pos a vivo:Position ; \n" +
                "       vivo:relates ?childOrg, ?person .\n" +
                "?person a foaf:Person .\n" +
                "}\n" +
                "UNION {" +
                "?org a foaf:Organization ; \n" +
                "      obo:BFO_0000051 ?childOrg ;\n" +
                "      obo:BFO_0000051 ?grandChildOrg .\n" +
                "?grandChildOrg a foaf:Organization ; \n"+
                "   vivo:relatedBy ?pos . \n" +
                "?pos a vivo:Position ; \n" +
                "       vivo:relates ?grandChildOrg, ?person .\n" +
                "?person a foaf:Person .\n" +
                "}\n" +
                "}";
        ParameterizedSparqlString q2 = this.storeUtils.getQuery(rq);
        q2.setIri("org", orgUri);
        String query = q2.toString();
        log.debug("Collab query:\n" + query);
        ArrayList<HashMap> results = this.storeUtils.getFromStore(query);
        for (HashMap row : results) {
            members.add(row.get("person"));
        }
        return members;
    }

}
