package org.fredhutch.controller;

import com.google.common.base.Charsets;
import com.google.common.io.Resources;
import com.hp.hpl.jena.query.*;
import com.hp.hpl.jena.rdf.model.*;
import edu.cornell.mannlib.vitro.webapp.controller.VitroRequest;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.FreemarkerHttpServlet;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.UrlBuilder;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.ResponseValues;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.TemplateResponseValues;
import edu.cornell.mannlib.vitro.webapp.rdfservice.RDFServiceException;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * Created by ted on 5/14/16.
 */
public class PeopleBrowseController extends FreemarkerHttpServlet {

    private static final Log log = LogFactory.getLog(PeopleBrowseController.class);
    private static final String TEMPLATE = "person-browse.ftl";
    private static final String PEOPLE_MODEL_QUERY = "peopleBrowse/getModel.rq";
    private static final String ORDERED_PEOPLE_QUERY = "peopleBrowse/orderedPeople.rq";
    private static final String PERSON_POSITIONS_QUERY = "peopleBrowse/personPositions.rq";
    public static final String TMP_NAMESPACE = "http://localhost/tmp#";

    @Override
    protected ResponseValues processRequest(VitroRequest vreq) {
        log.debug("Generating the person browse model");
        String letter = "a";
//        if ( letter == null ) {
//            letter = "a";
//        }
        String path = vreq.getPathInfo();
        if (path != null) {
            String[] pathParts = path.split("/");
            if (pathParts.length >= 1) {
                letter = pathParts[1];
            }
        }
        //Get the tmp model for people and positions
        String rq = prepModelQuery(letter);
        Model positionsModel = runConstruct(rq, vreq);

        ArrayList<HashMap> people = getPeople(positionsModel, vreq);

        Map<String, Object> body = new HashMap<String, Object>();
        char[] alphabet = "abcdefghijklmnopqrstuvwxyz".toCharArray();
        body.put("alphabet", alphabet);
        body.put("letter", letter);
        body.put("people", people);
        body.put("baseUrl", UrlBuilder.getUrl("people-browse"));
        body.put("title", "People");
        return new TemplateResponseValues(TEMPLATE, body);
    }

    public static ArrayList<HashMap> getPeople(Model positionsModel, VitroRequest vreq) {
        ArrayList<HashMap> people = new ArrayList<HashMap>();
        String rq = readQuery(ORDERED_PEOPLE_QUERY);
        ParameterizedSparqlString q2 = new ParameterizedSparqlString();
        q2.setCommandText(rq);
        q2.setNsPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
        q2.setNsPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
        q2.setNsPrefix("tmp", "http://localhost/tmp#");
        String query = q2.toString();
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
                thisPerson.put("email", soln.getLiteral("email"));
                thisPerson.put("phone", soln.getLiteral("phone"));
                thisPerson.put("positions", getPositions(positionsModel, person, vreq));
                people.add(thisPerson);

            }
        } finally {
            qexec.close();
        }
        return people;
    }

    public static ArrayList<HashMap> getPositions(Model model, Resource person, VitroRequest vreq) {
        ArrayList<HashMap> positions = new ArrayList<HashMap>();
        String rawQuery = readQuery(PERSON_POSITIONS_QUERY);
        ParameterizedSparqlString q2 = new ParameterizedSparqlString();
        q2.setCommandText(rawQuery);
        q2.setNsPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
        q2.setNsPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
        q2.setNsPrefix("tmp", TMP_NAMESPACE);
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
                thisPosition.put("parentOrgName", soln.getLiteral("parentOrgName"));
                positions.add(thisPosition);
            }
        } finally {
            qexec.close();
        }
        return positions;
    }

    public static String prepModelQuery(String letter) {
        String rq = readQuery(PEOPLE_MODEL_QUERY);
        ParameterizedSparqlString q2 = new ParameterizedSparqlString();
        q2.setCommandText(rq);
        q2.setNsPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
        q2.setNsPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
        q2.setNsPrefix("tmp", TMP_NAMESPACE);
        q2.setLiteral("?startswith", letter);
        return q2.toString();
    }

    public static Model runConstruct(String rawQuery, VitroRequest vreq) {
        ParameterizedSparqlString q2 = new ParameterizedSparqlString();
        q2.setCommandText(rawQuery);
        q2.setNsPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
        q2.setNsPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
        q2.setNsPrefix("obo", "http://purl.obolibrary.org/obo/");
        q2.setNsPrefix("vcard", "http://www.w3.org/2006/vcard/ns#");
        q2.setNsPrefix("tmp", TMP_NAMESPACE);
        q2.setNsPrefix("foaf", "http://xmlns.com/foaf/0.1/");
        q2.setNsPrefix("vivo", "http://vivoweb.org/ontology/core#");
        q2.setNsPrefix("fhd", "http://vivo.fredhutch.org/ontology/display#");
        String query = q2.toString();
        log.debug("Construct Person model:\n" + query);
        Model results = ModelFactory.createDefaultModel();
        try {
            vreq.getRDFService().sparqlConstructQuery(query, results);
        } catch (RDFServiceException e) {
            e.printStackTrace();
        }
        return results;
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
