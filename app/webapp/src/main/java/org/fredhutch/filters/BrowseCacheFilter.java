package org.fredhutch.filters;

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
    private static final Boolean cacheBrowse = true;
    FilterConfig filterConfig = null;

    public void init(FilterConfig filterConfig) throws ServletException {
        this.filterConfig = filterConfig;
    }

    public void destroy() {
    }

    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) request;
        HttpServletResponse resp = (HttpServletResponse) response;

        //Build etag from full request URL and the letter.
        String path = req.getRequestURL().toString();
        String params = req.getParameter("letter");
        String thisEtag = cacheKey(path + params);
        log.debug("Generated etag: " + thisEtag);
        // check cache
        if (shouldCache(req, thisEtag)) {
            resp.addHeader("ETag", thisEtag);
            resp.sendError(HttpServletResponse.SC_NOT_MODIFIED, "Not Modified");
        } else {
            resp.addHeader("ETag", thisEtag);
        }
        chain.doFilter(req, resp);

    }

    private Boolean shouldCache(HttpServletRequest request, String thisEtag) {
        if (cacheBrowse.equals(false)) {
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
        Integer week = Calendar.getInstance().get(Calendar.DAY_OF_YEAR);
        return week.toString() + value;
    }

    private boolean isConditionalRequest(HttpServletRequest req) {
        if (req.getHeader("If-None-Match") == null) {
            return false;
        } else {
            return true;
        }
    }

    /*
        Calculate an ETAG for the incoming request and return true/false
        if this request should not be regenerated.
     */
    private static Boolean cached(String existing, String etag) {
        String key = cacheKey(existing);
        if ( key.equals(existing) ) {
            return true;
        } else {
            return false;
        }
    }

}
