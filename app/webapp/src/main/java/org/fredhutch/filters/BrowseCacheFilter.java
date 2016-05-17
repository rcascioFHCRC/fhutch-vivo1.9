package org.fredhutch.filters;

import edu.cornell.mannlib.vitro.webapp.config.ConfigurationProperties;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Calendar;

/**
 * Generate ETags for the custom browse pages to faciltate caching..
 */
public class BrowseCacheFilter implements Filter {
    private static final Log log = LogFactory.getLog(BrowseCacheFilter.class);
    private static final String PROPERTY_ENABLE_CACHING = "http.createCacheHeaders";

    private ServletContext ctx;
    private boolean enabled;

    public void init(FilterConfig fc) throws ServletException {
        ctx = fc.getServletContext();
        ConfigurationProperties props = ConfigurationProperties.getBean(ctx);
        enabled = Boolean.valueOf(props.getProperty(PROPERTY_ENABLE_CACHING));
    }

    public void destroy() {
    }

    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) request;
        HttpServletResponse resp = (HttpServletResponse) response;

        //Build etag from full request URL.
        String url = ((HttpServletRequest)request).getRequestURL().toString();
        String thisEtag = cacheKey(url);
        log.debug("Generated etag: " + thisEtag);
        // check cache
        if (shouldCache(req, thisEtag)) {
            resp.addHeader("ETag", thisEtag);
            resp.sendError(HttpServletResponse.SC_NOT_MODIFIED, "Not Modified");
        } else {
            //Should we send cache headers?
            if (shouldCache(req, thisEtag)) {
                resp.addHeader("ETag", thisEtag);
            }
        }
        chain.doFilter(req, resp);

    }

    private Boolean shouldCache(HttpServletRequest request, String thisEtag) {
        if (enabled == false) {
            return false;
        }
        else if (!isConditionalRequest(request)) {
            return false;
        }
        else {
            String incoming = incomingEtag(request);
            if (thisEtag.equals(incoming)) {
                return true;
            } else {
                return false;
            }
        }
    }

    private String incomingEtag(HttpServletRequest request) {
        return request.getHeader("If-None-Match");
    }

    private static String cacheKey(String value) {
        Integer day = Calendar.getInstance().get(Calendar.DAY_OF_YEAR);
        //convert date value to string and the incoming value to a
        //string of the hash code.
        return day.toString() + String.valueOf(value.hashCode());
    }

    private boolean isConditionalRequest(HttpServletRequest req) {
        if (req.getHeader("If-None-Match") == null) {
            return false;
        } else {
            return true;
        }
    }

}
