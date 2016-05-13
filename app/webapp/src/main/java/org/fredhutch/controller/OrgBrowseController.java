package org.fredhutch.controller;

/**
 * Created by ted on 4/9/16.
 */
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import com.google.common.base.Charsets;
import com.google.common.io.Resources;
import com.hp.hpl.jena.query.ParameterizedSparqlString;
import com.hp.hpl.jena.rdf.model.*;
import com.hp.hpl.jena.vocabulary.RDF;
import com.hp.hpl.jena.vocabulary.RDFS;
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
    private static final String TEMPLATE_DEFAULT = "org-browse.ftl";
    public static final String SUB_ORG_PROPERTY = "http://purl.obolibrary.org/obo/BFO_0000050";
    public static final String TOP_ORG = "http://vivo.fredhutch.org/individual/c638881";
    public static final String TMP_NAMESPACE = "http://localhost/tmp#";

    @Override
    protected ResponseValues processRequest(VitroRequest vreq) {
        Model model = ModelFactory.createDefaultModel();
        Resource fhcrc = model.createResource(TOP_ORG);
        Resource parentResource = model.createResource(TMP_NAMESPACE + "Parent");
        Property hasChild = model.createProperty(SUB_ORG_PROPERTY);

        log.debug("Generating org browse model");
        Model orgModel = getOrgModel(vreq, fhcrc);

        //ArrayList<HashMap> subs = getChildOrgs(orgModel, fhcrc);
        ArrayList<HashMap> orgTree = new ArrayList<HashMap>();

        ResIterator iter = orgModel.listResourcesWithProperty(RDF.type, parentResource);
        if (iter.hasNext()) {
            while (iter.hasNext()) {
                HashMap thisOrg = new HashMap();
                Resource parent = iter.nextResource();
                String parentName = parent.getProperty(RDFS.label).getObject().toString();
                ArrayList<HashMap> subs = getChildOrgs(orgModel, iter.nextResource(), vreq);
                thisOrg.put("uri", parent.getURI());
                thisOrg.put("url", getURL(parent.getURI().toString(), vreq));
                thisOrg.put("name", parentName);
                thisOrg.put("children", subs);
                orgTree.add(thisOrg);
                //Gson gson = new Gson();
                //String json = gson.toJson(subs);
                //System.out.println(json);
            }
        }
        Map<String, Object> body = new HashMap<String, Object>();
        body.put("tree", orgTree);
        body.put("title", "Organizations");

        return new TemplateResponseValues(TEMPLATE_DEFAULT, body);
    }

    public static ArrayList<HashMap> getChildOrgs(Model model, Resource uri, VitroRequest vreq) {
        Property hasChild = model.createProperty( TMP_NAMESPACE + "child" );
        NodeIterator iter = model.listObjectsOfProperty(uri, hasChild);
        ArrayList<HashMap> kids = new ArrayList<HashMap>();
        if (iter.hasNext()) {
            while (iter.hasNext()) {
                RDFNode stmt = iter.nextNode();
                HashMap org = new HashMap();
                String ouri = stmt.toString();
                org.put("uri", ouri);
                org.put("url", getURL(ouri, vreq));
                org.put("name", model.getResource(ouri).getProperty(RDFS.label).getObject().toString());
                kids.add(org);
            }
        }
        return kids;
    }

    public static Model getOrgModel (VitroRequest vreq, Resource topUri) {
        final ArrayList people = new ArrayList<String>();
        ParameterizedSparqlString q2 = new ParameterizedSparqlString();
        q2.setCommandText(
                "CONSTRUCT {\n" +
                        " ?o a tmp:Parent ;\n" +
                        "   rdfs:label ?oName ;\n" +
                        "   tmp:child ?o2 .\n" +
                        "?o2 rdfs:label ?oName2 \n" +
                        "}\n" +
                        "WHERE {\n" +
                        "?o a foaf:Organization obo:BFO_0000050 ?top ;\n" +
                        "       rdfs:label ?oName .\n" +
                        "OPTIONAL {\n" +
                        "   ?o2 obo:BFO_0000050 ?o ;\n" +
                        "     rdfs:label ?oName2 .\n" +
                        "}\n" +
                "}\n"
        );
        //q2.setBaseUri("http://example.org/base#");
        q2.setNsPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
        q2.setNsPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
        q2.setNsPrefix("tmp", TMP_NAMESPACE);
        q2.setNsPrefix("obo", "http://purl.obolibrary.org/obo/");
        q2.setNsPrefix("foaf", "http://xmlns.com/foaf/0.1/");
        q2.setIri("top", topUri.toString());
        String query = q2.toString();
        log.debug("Org browse query:\n" + query);

        Model model = ModelFactory.createDefaultModel();
        try {
            vreq.getRDFService().sparqlConstructQuery(query, model);
        } catch (RDFServiceException e) {
            e.printStackTrace();
        }
        return model;
    }

    public static String readQuery( String name ) {
        URL qurl = Resources.getResource(name);
        try {
            return Resources.toString(qurl, Charsets.UTF_8);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static String getLocalName( String uri) {
        Resource r = ResourceFactory.createResource(uri);
        return r.getLocalName();
    }

    public static String getURL( String uri, VitroRequest vreq ) {
        return UrlBuilder.getIndividualProfileUrl(uri, vreq);
    }
}
