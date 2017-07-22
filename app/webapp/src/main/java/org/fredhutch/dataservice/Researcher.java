package org.fredhutch.dataservice;

import com.google.common.base.Charsets;
import com.google.common.io.Resources;
import com.hp.hpl.jena.query.*;
import com.hp.hpl.jena.rdf.model.Literal;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Resource;
import edu.cornell.mannlib.vitro.webapp.config.ConfigurationProperties;
import edu.cornell.mannlib.vitro.webapp.controller.VitroRequest;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.UrlBuilder;
import edu.cornell.mannlib.vitro.webapp.rdfservice.RDFServiceException;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.fredhutch.utils.StoreUtils;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.net.URL;
import java.util.HashMap;

/**
 * Return info about a researcher as JSON
 */
public class Researcher extends HttpServlet {

    private static final Log log = LogFactory.getLog(Researcher.class.getName());
    private static final String PEOPLE_MODEL_QUERY = "peopleBrowse/getModel.rq";
    private static final String ORDERED_PEOPLE_QUERY = "peopleBrowse/orderedPeople.rq";
    private static final String PERSON_POSITIONS_QUERY = "peopleBrowse/personPositions.rq";
    private static String namespace;
    private StoreUtils storeUtils;


    protected final void doGet(HttpServletRequest req, HttpServletResponse response) throws ServletException, IOException {
        VitroRequest vreq = new VitroRequest(req);
        ConfigurationProperties props = ConfigurationProperties.getBean(vreq);
        namespace = props.getProperty("Vitro.defaultNamespace");
        String path = vreq.getPathInfo();
        log.debug("Request path" + path);
        if (path != null) {
            //setup storeUtils
            this.storeUtils = new StoreUtils();
            this.storeUtils.setRdfService(namespace, vreq.getRDFService());

            String[] pathParts = path.split("/");
            log.debug("Recent items service: " + pathParts[1]);
            String requestLocalName = pathParts[1];
            log.debug("Request path" + requestLocalName);
            JSONObject card = getCard(requestLocalName, vreq);
            response.setContentType("application/json");
            response.setCharacterEncoding("UTF-8");
            response.getWriter().write(card.toString());
        } else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }

    }

    /**
     *
     * @param vreq
     * @return JSONArray of People
     */
    private JSONObject getCard(String localName, VitroRequest vreq) {
        final JSONArray person = new JSONArray();
        //Get the tmp model for people and positions
        String rq = prepModelQuery(namespace + localName);
        Model positionsModel = this.storeUtils.constructFromStore(rq);
        return getPeople(positionsModel, vreq);
    }

    private JSONObject getPeople(Model positionsModel, VitroRequest vreq) {
        JSONObject people = new JSONObject();
        String rq = readQuery(ORDERED_PEOPLE_QUERY);
        ParameterizedSparqlString q = this.storeUtils.getQuery(rq);
        String query = q.toString();

        log.debug("Ordered people query:\n" + query);
        QueryExecution qexec = QueryExecutionFactory.create(query, positionsModel);
        try {
            ResultSet results = qexec.execSelect();
            while ( results.hasNext() ) {
                HashMap thisPerson = new HashMap();
                QuerySolution soln = results.nextSolution();
                Literal name = soln.getLiteral("name");
                Resource person = soln.getResource("p");
                thisPerson.put("name", name.toString());
                thisPerson.put("uri", person.toString());
                thisPerson.put("url", getURL(person.toString(), vreq));
                thisPerson.put("picture", soln.getLiteral("picture"));
                thisPerson.put("description", soln.getLiteral("description"));
                thisPerson.put("positions", getPositions(positionsModel, person, vreq));
                try {
                    people.put("profile", thisPerson);
                } catch (JSONException e) {
                    e.printStackTrace();
                }

            }
        } finally {
            qexec.close();
        }
        return people;
    }

    public String prepModelQuery(String personUri) {
        String rq = readQuery(PEOPLE_MODEL_QUERY);
        ParameterizedSparqlString q = this.storeUtils.getQuery(rq);
        q.setIri("?p", personUri);
        return q.toString();
    }

    public JSONArray getPositions(Model model, Resource person, VitroRequest vreq) {
        JSONArray positions = new JSONArray();
        String rawQuery = readQuery(PERSON_POSITIONS_QUERY);
        ParameterizedSparqlString q2 = this.storeUtils.getQuery(rawQuery);
        q2.setIri("person", person.toString());
        String query = q2.toString();
        log.debug("Positions query:\n" + query);
        QueryExecution qexec = QueryExecutionFactory.create(query, model);
        try {
            ResultSet results = qexec.execSelect();
            while ( results.hasNext() ) {
                HashMap thisPosition = new HashMap();
                QuerySolution soln = results.nextSolution();
                String orgUri = soln.getResource("org").toString();
                thisPosition.put("title", soln.getLiteral("title").toString());
                thisPosition.put("org", orgUri);
                thisPosition.put("orgName", soln.getLiteral("orgName").toString());
                thisPosition.put("url", getURL(orgUri, vreq));
                positions.put(thisPosition);
            }
        } finally {
            qexec.close();
        }
        return positions;
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