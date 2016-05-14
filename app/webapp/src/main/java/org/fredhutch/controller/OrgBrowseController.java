package org.fredhutch.controller;

/**
 * Organizational browse. Tree starting with top level org..
 */
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import com.google.common.base.Charsets;
import com.google.common.io.Resources;
import com.hp.hpl.jena.query.*;
import com.hp.hpl.jena.rdf.model.*;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.FreemarkerHttpServlet;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.UrlBuilder;
import edu.cornell.mannlib.vitro.webapp.rdfservice.RDFServiceException;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import edu.cornell.mannlib.vitro.webapp.controller.VitroRequest;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.ResponseValues;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.TemplateResponseValues;

public class OrgBrowseController extends FreemarkerHttpServlet {

    private static final Log log = LogFactory.getLog(OrgBrowseController.class);
    private static final String TEMPLATE = "org-browse.ftl";
    public static final String SUB_ORG_PROPERTY = "http://purl.obolibrary.org/obo/BFO_0000050";
    public static final String TOP_ORG = "http://vivo.fredhutch.org/individual/c638881";
    public static final String TMP_NAMESPACE = "http://localhost/tmp#";
    public static final String CHILD_QUERY = "orgBrowse/getChildren.rq";
    public static final String ORG_MODEL_QUERY = "orgBrowse/getStructure.rq";

    @Override
    protected ResponseValues processRequest(VitroRequest vreq) {
        log.debug("Generating org browse model");
        //Get the tmp model for org structure
        String rq = readQuery(ORG_MODEL_QUERY);
        Model orgModel = runConstruct(rq, vreq);

        //Starting with top level org uri, get orgs with
        Resource topUri = ResourceFactory.createResource(TOP_ORG);
        //Get child orgs
        ArrayList<HashMap> orgTree = getChildren(orgModel, topUri, vreq);

        Map<String, Object> body = new HashMap<String, Object>();
        body.put("tree", orgTree);
        body.put("title", "Organizations");
        return new TemplateResponseValues(TEMPLATE, body);
    }

    public static ArrayList<HashMap> getChildren(Model model, Resource parent, VitroRequest vreq) {
        ArrayList<HashMap> kids = new ArrayList<HashMap>();
        String rawQuery = readQuery(CHILD_QUERY);
        ParameterizedSparqlString q2 = new ParameterizedSparqlString();
        q2.setCommandText(rawQuery);
        q2.setNsPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
        q2.setNsPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
        q2.setNsPrefix("tmp", TMP_NAMESPACE);
        q2.setIri("parent", parent.toString());
        String query = q2.toString();
        log.debug("Org children query:\n" + query);
        QueryExecution qexec = QueryExecutionFactory.create(query, model);
        try {
            ResultSet results = qexec.execSelect();
            while ( results.hasNext() ) {
                HashMap thisOrg = new HashMap();
                QuerySolution soln = results.nextSolution();
                Literal name = soln.getLiteral("name");
                String ouri = soln.getResource("o").toString();
                thisOrg.put("name", name.toString());
                thisOrg.put("uri", ouri);
                thisOrg.put("url", getURL(ouri, vreq));
                ArrayList<HashMap> gc = getChildren(model, ResourceFactory.createResource(ouri), vreq);
                if (gc.isEmpty()) {
                    thisOrg.put("children", new ArrayList<HashMap>());
                    kids.add(thisOrg);
                } else {
                    thisOrg.put("children", gc);
                    kids.add(thisOrg);
                }
            }
        } finally {
            qexec.close();
        }
        return kids;
    }

    public static Model runConstruct(String rawQuery, VitroRequest vreq) {
        ParameterizedSparqlString q2 = new ParameterizedSparqlString();
        q2.setCommandText(rawQuery);
        q2.setNsPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
        q2.setNsPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
        q2.setNsPrefix("tmp", TMP_NAMESPACE);
        q2.setNsPrefix("obo", "http://purl.obolibrary.org/obo/");
        q2.setNsPrefix("foaf", "http://xmlns.com/foaf/0.1/");
        String query = q2.toString();
        log.debug("Construct Org model:\n" + query);
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
