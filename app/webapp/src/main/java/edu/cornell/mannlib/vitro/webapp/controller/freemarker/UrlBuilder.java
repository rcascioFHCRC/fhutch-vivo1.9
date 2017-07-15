package edu.cornell.mannlib.vitro.webapp.controller.freemarker;

import edu.cornell.mannlib.vitro.webapp.beans.Individual;
import edu.cornell.mannlib.vitro.webapp.beans.IndividualImpl;
import edu.cornell.mannlib.vitro.webapp.controller.VitroRequest;
import edu.cornell.mannlib.vitro.webapp.dao.WebappDaoFactory;
import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.net.URLEncoder;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.fredhutch.utils.Config;

public class UrlBuilder {
    private static final Log log = LogFactory.getLog(UrlBuilder.class.getName());
    protected static String contextPath = null;

    private UrlBuilder() {
    }

    public static String getHomeUrl() {
        return getUrl("");
    }

    public static String getBaseUrl() {
        return contextPath;
    }

    public static String getLoginUrl() {
        return getUrl(UrlBuilder.Route.AUTHENTICATE, new String[]{"return", "true"});
    }

    public static String getLogoutUrl() {
        return getUrl(UrlBuilder.Route.LOGOUT);
    }

    public static String getUrl(String path) {
        if(!path.isEmpty() && !path.startsWith("/")) {
            path = "/" + path;
        }

        path = contextPath + path;
        return path.isEmpty()?"/":path;
    }

    public static String getUrl(UrlBuilder.Route route) {
        return getUrl(route.path());
    }

    public static String getUrl(String path, String... params) {
        UrlBuilder.ParamMap urlParams = new UrlBuilder.ParamMap(params);
        return getUrl(path, urlParams);
    }

    public static String getUrl(UrlBuilder.Route route, String... params) {
        return getUrl(route.path(), params);
    }

    public static String getUrl(String path, UrlBuilder.ParamMap params) {
        path = getPath(path, params);
        return getUrl(path);
    }

    public static String getUrl(UrlBuilder.Route route, UrlBuilder.ParamMap params) {
        return getUrl(route.path(), params);
    }

    public static String getPath(String path, UrlBuilder.ParamMap params) {
        return addParams(path, params, "?");
    }

    private static String addParams(String url, UrlBuilder.ParamMap params, String glue) {
        for(Iterator var3 = params.keySet().iterator(); var3.hasNext(); glue = "&") {
            String key = (String)var3.next();
            String value = (String)params.get(key);
            value = value == null?"":urlEncode(value);
            url = url + glue + key + "=" + value;
        }

        return url;
    }

    public static String addParams(String url, UrlBuilder.ParamMap params) {
        String glue = url.contains("?")?"&":"?";
        return addParams(url, params, glue);
    }

    public static String addParams(String url, String... params) {
        return addParams(url, new UrlBuilder.ParamMap(params));
    }

    public static String addParams(String url, List<String> params) {
        return addParams(url, new UrlBuilder.ParamMap(params));
    }

    public static String getPath(UrlBuilder.Route route, UrlBuilder.ParamMap params) {
        return getPath(route.path(), params);
    }

    public static String getIndividualProfileUrl(Individual individual, VitroRequest vreq) {
        WebappDaoFactory wadf = vreq.getWebappDaoFactory();
        String profileUrl = null;

        try {
            String specialParams = individual.getLocalName();
            String namespace = individual.getNamespace();
            String defaultNamespace = wadf.getDefaultNamespace();
            if (individual.getLocalName().equals(Config.topOrgLocalName)) {
                profileUrl = getUrl("org/" + specialParams);
            } else if(defaultNamespace.equals(namespace)) {
                profileUrl = getUrl(UrlBuilder.Route.DISPLAY.path() + "/" + specialParams);
            } else if(wadf.getApplicationDao().isExternallyLinkedNamespace(namespace)) {
                log.debug("Found externally linked namespace " + namespace);
                profileUrl = namespace + specialParams;
            } else {
                UrlBuilder.ParamMap params = new UrlBuilder.ParamMap(new String[]{"uri", individual.getURI()});
                profileUrl = getUrl(UrlBuilder.Route.INDIVIDUAL.path(), params);
            }
        } catch (Exception var8) {
            log.warn(var8);
            return null;
        }

        if(profileUrl != null) {
            LinkedHashMap specialParams1 = getModelParams(vreq);
            if(specialParams1.size() != 0) {
                profileUrl = addParams(profileUrl, new UrlBuilder.ParamMap(specialParams1));
            }
        }

        return profileUrl;
    }

    public static String getIndividualProfileUrl(String individualUri, VitroRequest vreq) {
        return getIndividualProfileUrl((Individual)(new IndividualImpl(individualUri)), vreq);
    }

    public static boolean isUriInDefaultNamespace(String individualUri, VitroRequest vreq) {
        return isUriInDefaultNamespace(individualUri, vreq.getWebappDaoFactory());
    }

    public static boolean isUriInDefaultNamespace(String individualUri, WebappDaoFactory wadf) {
        return isUriInDefaultNamespace(individualUri, wadf.getDefaultNamespace());
    }

    public static boolean isUriInDefaultNamespace(String individualUri, String defaultNamespace) {
        try {
            IndividualImpl e = new IndividualImpl(individualUri);
            String namespace = e.getNamespace();
            return defaultNamespace.equals(namespace);
        } catch (Exception var4) {
            log.warn(var4);
            return false;
        }
    }

    public static String urlEncode(String str) {
        String encoding = "UTF-8";
        String encodedUrl = null;

        try {
            encodedUrl = URLEncoder.encode(str, encoding);
        } catch (UnsupportedEncodingException var4) {
            log.error("Error encoding url " + str + " with encoding " + encoding + ": Unsupported encoding.");
        }

        return encodedUrl;
    }

    public static String urlDecode(String str) {
        String encoding = "UTF-8";
        String decodedUrl = null;

        try {
            decodedUrl = URLDecoder.decode(str, encoding);
        } catch (UnsupportedEncodingException var4) {
            log.error("Error decoding url " + str + " with encoding " + encoding + ": Unsupported encoding.");
        }

        return decodedUrl;
    }

    public static LinkedHashMap<String, String> getModelParams(VitroRequest vreq) {
        LinkedHashMap specialParams = new LinkedHashMap();
        if(vreq != null) {
            String useMenuModelParam = vreq.getParameter("switchToDisplayModel");
            String useMainModelUri = vreq.getParameter("useThisModel");
            String useTboxModelUri = vreq.getParameter("useThisTboxModel");
            String useDisplayModelUri = vreq.getParameter("useThisDisplayModel");
            if(useMenuModelParam != null && !useMenuModelParam.isEmpty()) {
                specialParams.put("switchToDisplayModel", useMenuModelParam);
            } else if(useMainModelUri != null && !useMainModelUri.isEmpty()) {
                specialParams.put("useThisModel", useMainModelUri);
                if(useTboxModelUri != null && !useTboxModelUri.isEmpty()) {
                    specialParams.put("useThisTboxModel", useTboxModelUri);
                }

                if(useDisplayModelUri != null && !useDisplayModelUri.isEmpty()) {
                    specialParams.put("useThisDisplayModel", useDisplayModelUri);
                }
            }
        }

        return specialParams;
    }

    public static class ParamMap extends LinkedHashMap<String, String> {
        private static final long serialVersionUID = 1L;

        public ParamMap() {
        }

        public ParamMap(String... strings) {
            int stringCount = strings.length;

            for(int i = 0; i < stringCount && i != stringCount - 1; i += 2) {
                if(strings[i + 1] != null) {
                    this.put(strings[i], strings[i + 1]);
                }
            }

        }

        public ParamMap(List<String> strings) {
            this((String[])((String[])strings.toArray()));
        }

        public ParamMap(Map<String, String> map) {
            this.putAll(map);
        }

        public void put(String key, int value) {
            this.put(key, String.valueOf(value));
        }

        public void put(String key, boolean value) {
            this.put(key, String.valueOf(value));
        }

        public void put(UrlBuilder.ParamMap params) {
            Iterator var2 = params.keySet().iterator();

            while(var2.hasNext()) {
                String key = (String)var2.next();
                this.put(key, params.get(key));
            }

        }
    }

    public static enum JavaScript {
        CUSTOM_FORM_UTILS("/js/customFormUtils.js"),
        JQUERY("/js/jquery.js"),
        JQUERY_UI("/js/jquery-ui/js/jquery-ui-1.8.9.custom.min.js"),
        UTILS("/js/utils.js");

        private final String path;

        private JavaScript(String path) {
            this.path = path;
        }

        public String path() {
            return this.path;
        }

        public String toString() {
            return this.path;
        }
    }

    public static enum Css {
        CUSTOM_FORM("/edit/forms/css/customForm.css"),
        JQUERY_UI("/js/jquery-ui/css/smoothness/jquery-ui-1.8.9.custom.css");

        private final String path;

        private Css(String path) {
            this.path = path;
        }

        public String path() {
            return this.path;
        }

        public String toString() {
            return this.path;
        }
    }

    public static enum Route {
        ABOUT("/about"),
        AUTHENTICATE("/authenticate"),
        BROWSE("/browse"),
        CONTACT("/contact"),
        DATA_PROPERTY_EDIT("/datapropEdit"),
        DISPLAY("/display"),
        INDIVIDUAL("/individual"),
        INDIVIDUAL_EDIT("/entityEdit"),
        INDIVIDUAL_LIST("/individuallist"),
        LOGIN("/login"),
        LOGOUT("/logout"),
        OBJECT_PROPERTY_EDIT("/propertyEdit"),
        SEARCH("/search"),
        SITE_ADMIN("/siteAdmin"),
        TERMS_OF_USE("/termsOfUse"),
        VISUALIZATION("/visualization"),
        VISUALIZATION_SHORT("/vis"),
        VISUALIZATION_AJAX("/visualizationAjax"),
        VISUALIZATION_DATA("/visualizationData"),
        EDIT_REQUEST_DISPATCH("/editRequestDispatch");

        private final String path;

        private Route(String path) {
            this.path = path;
        }

        public String path() {
            return this.path;
        }

        public String url() {
            return UrlBuilder.getUrl(this.path);
        }

        public String url(UrlBuilder.ParamMap params) {
            return UrlBuilder.getUrl(this.path, params);
        }

        public String toString() {
            return this.path();
        }
    }
}
