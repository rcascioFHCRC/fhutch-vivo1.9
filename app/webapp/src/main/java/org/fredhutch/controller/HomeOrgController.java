package org.fredhutch.controller;


import edu.cornell.mannlib.vitro.webapp.config.ConfigurationProperties;
import edu.cornell.mannlib.vitro.webapp.controller.VitroRequest;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.FreemarkerHttpServlet;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.UrlBuilder;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.ResponseValues;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.TemplateResponseValues;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.jena.query.ParameterizedSparqlString;
import org.apache.jena.rdf.model.Model;
import org.fredhutch.utils.StoreUtils;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class HomeOrgController extends FreemarkerHttpServlet {

    private static final Log log = LogFactory.getLog(PeopleBrowseController.class);
    private static final String TEMPLATE = "home-org.ftl";
    private static String namespace;
    private StoreUtils storeUtils;

    @Override
    protected ResponseValues processRequest(VitroRequest vreq) {
        ConfigurationProperties props = ConfigurationProperties.getBean(vreq);
        namespace = props.getProperty("Vitro.defaultNamespace");

        String localName = null;
        String path = vreq.getPathInfo();
        if (path != null) {
            String[] pathParts = path.split("/");
            if (pathParts.length >= 1) {
                localName = pathParts[1];
            }
        }
        String orgUri = namespace + localName;

        //setup storeUtils
        this.storeUtils = new StoreUtils();
        this.storeUtils.setRdfService(namespace, vreq.getRDFService());

        String rq = "" +
                "CONSTRUCT {" +
                "   ?org tmp:name ?name" +
                "}" +
                "WHERE {" +
                "   ?org a fhd:Organization ;" +
                "       rdfs:label ?name" +
                "}";
        ParameterizedSparqlString q = this.storeUtils.getQuery(rq);
        q.setIri("org", orgUri);
        String query = q.toString();
        Model scratch = this.storeUtils.constructFromStore(query);

        String srq = "SELECT ?name WHERE { ?org tmp:name ?name }";
        ParameterizedSparqlString q2 = this.storeUtils.getQuery(srq);
        q2.setCommandText(srq);
        ArrayList<HashMap> results = this.storeUtils.getFromModel(q2.toString(), scratch);
        HashMap rsp = results.get(0);

        Map<String, Object> body = new HashMap<String, Object>();
        body.put("title", rsp.get("name"));
        body.put("people", getPeople(orgUri));
        //add alpha browse
        char[] alphabet = "abcdefghijklmnopqrstuvwxyz".toCharArray();
        body.put("alphabet", alphabet);
        body.put("baseUrl", UrlBuilder.getUrl("people-browse"));

        return new TemplateResponseValues(TEMPLATE, body);
    }

    private ArrayList<HashMap> getPeople(String orgUri) {
        String peopleQuery = "" +
                "select ?p ?name ?pTitle ?position ?title ?picture \n" +
                "where {\n" +
                "    {\n" +
                "        ?org vivo:relatedBy ?position .\n" +
                "        ?position a vivo:FacultyAdministrativePosition ;\n" +
                "                  rdfs:label ?title .\n" +
                "        ?p a foaf:Person ;\n" +
                "            rdfs:label ?name ;\n" +
                "            vivo:relatedBy ?position .\n" +
                "        OPTIONAL {?p fhd:image ?picture }\n" +
                "        OPTIONAL {\n" +
                "            ?p obo:ARG_2000028 ?vci .\n" +
                "            ?vci vcard:hasTitle ?ti .\n" +
                "            ?ti vcard:title ?pTitle .\n" +
                "        }\n" +
                "    }\n" +
                "}\n" +
                "ORDER BY DESC(?title) ?name";
        ParameterizedSparqlString q2 = this.storeUtils.getQuery(peopleQuery);
        q2.setIri("org", orgUri);
        String query = q2.toString();
        ArrayList<HashMap> peopleResults = this.storeUtils.getFromStore(query);
        return peopleResults;
    }
}
