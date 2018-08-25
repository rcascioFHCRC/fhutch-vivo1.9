package org.fredhutch.controller;

import edu.cornell.mannlib.vitro.webapp.config.ConfigurationProperties;
import edu.cornell.mannlib.vitro.webapp.controller.VitroRequest;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.FreemarkerHttpServlet;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.ResponseValues;
import edu.cornell.mannlib.vitro.webapp.controller.freemarker.responsevalues.TemplateResponseValues;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.jena.query.ParameterizedSparqlString;
import org.fredhutch.utils.StoreUtils;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * Organization Collaboration Visualization
 */
public class OrgCollabVizController  extends FreemarkerHttpServlet {
    private static final Log log = LogFactory.getLog(OrgCollabVizController.class);
    private static final String TEMPLATE = "org-collabs.ftl";
    private StoreUtils storeUtils;

    @Override
    protected ResponseValues processRequest(VitroRequest vreq) {
        log.debug("Generating org collab viz.");
        ConfigurationProperties props = ConfigurationProperties.getBean(vreq);
        String baseURL = vreq.getContextPath();
        String namespace = props.getProperty("Vitro.defaultNamespace");
        String path = vreq.getPathInfo();
        String[] pathParts = path.split("/");
        //setup storeUtils
        this.storeUtils = new StoreUtils();
        this.storeUtils.setRdfService(namespace, vreq.getRDFService());
        String ln = pathParts[1];
        String orgUri = namespace + ln;
        HashMap orgInfo = getOrgInfo(orgUri);
        Map<String, Object> body = new HashMap<>();
        body.put("title", "Organizational Collaborators");
        body.put("name", orgInfo.get("name"));
        body.put("localName", ln);
        body.put("overview", orgInfo.get("overview"));
        body.put("baseURL", baseURL);
        return new TemplateResponseValues(TEMPLATE, body);
    }

    /*  org info */
    private HashMap getOrgInfo(String orgUri) {
        log.debug("Running org query");
        String rq = "" +
                "SELECT ?name ?overview \n" +
                "WHERE { \n" +
                "   ?org a foaf:Organization ; \n" +
                "       rdfs:label ?name . \n" +
                "OPTIONAL { ?org vivo:overview ?overview } \n" +
                "}";
        ParameterizedSparqlString q2 = this.storeUtils.getQuery(rq);
        q2.setIri("org", orgUri);
        String query = q2.toString();
        log.debug("Recent query:\n" + query);
        ArrayList<HashMap> rsp = this.storeUtils.getFromStore(query);
        return rsp.get(0);
    }
}
