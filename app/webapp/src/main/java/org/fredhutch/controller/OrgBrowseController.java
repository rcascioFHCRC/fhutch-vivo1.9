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
import edu.cornell.mannlib.vitro.webapp.config.ConfigurationProperties;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.FreemarkerHttpServlet;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.UrlBuilder;
import edu.cornell.mannlib.vitro.webapp.rdfservice.RDFServiceException;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import edu.cornell.mannlib.vitro.webapp.controller.VitroRequest;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.ResponseValues;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.TemplateResponseValues;

import org.fredhutch.utils.Config;

public class OrgBrowseController extends FreemarkerHttpServlet {

    private static final Log log = LogFactory.getLog(OrgBrowseController.class);
    private static final String TEMPLATE = "org-browse.ftl";
    private static String namespace;
    public static final String SUB_ORG_PROPERTY = "http://purl.obolibrary.org/obo/BFO_0000050";
    public static final String FHD_PREFIX = "http://vivo.fredhutch.org/ontology/display#";
    public static final String TMP_NAMESPACE = "http://localhost/tmp#";
    public static final String CHILD_QUERY = "orgBrowse/getChildren.rq";
    public static final String CHILD_QUERY_BY_TYPE = "orgBrowse/getChildrenByType.rq";
    public static final String ORG_MODEL_QUERY = "orgBrowse/getStructure.rq";
    public static final Resource divisionUri = ResourceFactory.createResource(FHD_PREFIX + "Division");
    public static final Resource sciInitUri = ResourceFactory.createResource(FHD_PREFIX + "ScientificInitiative");
    public static final Resource ircUri = ResourceFactory.createResource(FHD_PREFIX + "InterdisciplinaryResearchCenter");

    @Override
    protected ResponseValues processRequest(VitroRequest vreq) {
        ConfigurationProperties props = ConfigurationProperties.getBean(vreq);
        namespace = props.getProperty("Vitro.defaultNamespace");
        String topOrg = namespace + Config.topOrgLocalName;
        log.debug("Generating org browse model");
        //Get the tmp model for org structure
        String rq = readQuery(ORG_MODEL_QUERY);
        Model orgModel = runConstruct(rq, vreq);

        //Starting with top level org uri, get orgs with
        Resource topUri = ResourceFactory.createResource(topOrg);
        //Get child orgs
//        ArrayList<HashMap> orgTree = getChildren(orgModel, topUri, vreq);
        //Divisions and children
        ArrayList<HashMap> divisionTree = getChildrenByType(orgModel, divisionUri, vreq);
        //Sci initiatives
        ArrayList<HashMap> sciITree = getChildrenByType(orgModel, sciInitUri, vreq);
        //InterdisciplinaryResearchCenter
        ArrayList<HashMap> ircTree = getChildrenByType(orgModel, ircUri, vreq);

        Map<String, Object> body = new HashMap<String, Object>();
        body.put("title", "Organizations");
        //body.put("tree", orgTree);
        body.put("divisions", divisionTree);
        body.put("sciInit", sciITree);
        body.put("irc", ircTree);
        body.put("topUrl", getURL(topOrg, vreq));
        return new TemplateResponseValues(TEMPLATE, body);
    }

    /**
     * Generic browse tree generator given a Jena model and parent URI.
     * @param model
     * @param parent
     * @param vreq
     * @return
     */
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
                thisOrg.put("name", name.getString());
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

    /**
     * Browse tree generator based on a type uri and RDF model
     *
     * @param model
     * @param orgType
     * @param vreq
     * @return
     */
    public static ArrayList<HashMap> getChildrenByType(Model model, Resource orgType, VitroRequest vreq) {
        ArrayList<HashMap> kids = new ArrayList<HashMap>();
        String rawQuery = readQuery(CHILD_QUERY_BY_TYPE);
        ParameterizedSparqlString q2 = new ParameterizedSparqlString();
        q2.setCommandText(rawQuery);
        q2.setNsPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
        q2.setNsPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
        q2.setNsPrefix("tmp", TMP_NAMESPACE);
        q2.setIri("orgType", orgType.toString());
        //q2.setIri("parent", parent.toString());
        String query = q2.toString();
        log.debug("Org children by type query:\n" + query);
        QueryExecution qexec = QueryExecutionFactory.create(query, model);
        try {
            ResultSet results = qexec.execSelect();
            while ( results.hasNext() ) {
                HashMap thisOrg = new HashMap();
                QuerySolution soln = results.nextSolution();
                Literal name = soln.getLiteral("name");
                String ouri = soln.getResource("o").toString();
                thisOrg.put("name", name.getString());
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
        q2.setNsPrefix("fhd", FHD_PREFIX);
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
