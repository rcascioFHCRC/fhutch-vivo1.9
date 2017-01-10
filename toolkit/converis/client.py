"""
Converis web services client
"""

from datetime import datetime
import os
import logging
import time


import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError


import requests
from requests.exceptions import ChunkedEncodingError

logger = logging.getLogger("converis_client")

# disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Set Converis URL globally from environment variable
CONVERIS_URL = os.environ['CONVERIS_URL'].rstrip('/') + '/'


def convert_date(raw):
    """
    Converis string date to Python date conversion.
    """
    return datetime.strptime(raw, '%Y-%m-%d').date()


def get_response(url):
    """
    HTTP requests for resource objects. Shared by
    InfoObject and RelatedObjects.

    Will try to load URL once and if a redirect is found,
    try again.

    """
    attempts = 0
    rsp = None
    while True:
        if attempts != 0:
            logger.warn("Retrying request for: {}".format(url))
        if attempts >= 2:
            logger.warn("Two attempts failed to fetch and parse: {}".format(url))
            break
        logger.debug("Requesting: {}".format(url))
        rsp = requests.get(url, verify=False)
        if rsp.status_code == 404:
            logger.error("404 - data not found: {}".format(url))
            break
        elif rsp.status_code == 500:
            logger.error("500 error -data not found: {}".format(url))
            break
        # Redirects indicate the id wasn't found.
        elif 302 in [r.status_code for r in rsp.history]:
            logger.warn("302 - redirect found in response. Will wait before retrying: {}".format(url))
            attempts += 1
            time.sleep(1)
            continue
        break
    return rsp


def get_filtered_response(query, start, stop):
    """
    HTTP utility for making requests to the filter engine.
    """
    logger.debug("Query:\n{}\n".format(query))
    rsp = requests.put(
        CONVERIS_URL + "ws/public/infoobject/getfiltered/" + "{}/{}".format(start,stop),
        data=query,
        verify=False
    )
    try:
        logger.debug("Response from cache {}".format(rsp.from_cache))
    except AttributeError:
        pass
    return rsp


class BaseEntity(object):
    """
    Abstract entity for Converis objects.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a class given dictionary passed
        as either args or kwargs.

        Some code from:
        http://stackoverflow.com/a/2466207
        """

        if kwargs.get('root') is not None:
            self.root = kwargs['root']
            del kwargs['root']

        try:
            attribs = self.attributes()
        except AttributeError:
            attribs = {}

        meta = attribs.copy()
        meta.update(kwargs)

        for key in meta:
            k = key.lower().replace(' ', '')
            value = meta[key]
            if type(value) != dict:
                value = value.strip()
            try:
                setattr(self, k, value)
            except AttributeError, e:
                raise


    def _read_attributes(self, base_element):
        d = {}
        for em in base_element:
            if em.attrib['language'] not in ['0', '1']:
                continue
            # Handle choice groups
            if em.attrib.get('disposition') == 'choicegroup':
                try:
                    value = {'cid': em.find('data').text, 'value': em.find('additionalInfo').text}
                # Some choice groups are empty unfortunately.
                except AttributeError:
                    continue
            else:
                value =  ";".join(em.itertext())
            if value != "":
                d[em.attrib['name']] = value
        return d

    def attributes(self):
        base_element = self.root.findall('attribute')
        attr = self._read_attributes(base_element)
        return attr


class Entity(BaseEntity):
    def __init__(self, ctype, cid, **kwargs):
        self.cid = cid
        url = CONVERIS_URL + 'ws/public/infoobject/get/{}/{}/'.format(ctype, cid)
        rsp = get_response(
            url
        )
        self.root = ET.fromstring(rsp.text.encode('utf-8', 'ignore'))
        # Call super class
        BaseEntity.__init__(self)


class EntityFilter(object):
    def __init__(self, query, start=0, stop=25):
        """
        Run a filter query. Optionally pass in a class to yield.
        """
        self.query = query
        logger.info("Executing filter query start {} stop {}.".format(start, stop))
        rsp = get_filtered_response(query, start, stop)
        self.text = rsp.text.encode('utf-8', 'ignore')
        try:
            self.filter_root = ET.fromstring(self.text)
            self.number = int(self.filter_root.attrib['size'])
        except ParseError:
            logger.error("Unable to parse query response:\n{}".format(self.text))
            self.filter_root = ET.Element("null")
            self.number = 0

    def __iter__(self):
        """
        For filter queries, run query with start stop params
        and yield an BaseEntity object with the Converis attributes.
        """
        try:
            for grp in self.filter_root.findall('infoObject'):
                yield BaseEntity(root=grp, cid=grp.attrib['id'])
        except AttributeError:
            logger.error("Unable to parse infoObject. \n {}".format(self.query))
            raise



class RelatedObject(BaseEntity):

    def __init__(self, ctype, c_id, relation, direction=None):
        self.ctype = ctype
        self.c_id = c_id
        self.relation = relation
        url = CONVERIS_URL.strip('/') + '/ws/public/infoobject/getrelated/{}/{}/{}'.format(self.ctype, c_id, relation)
        self.url = url
        if direction is not None:
            url += "?direction=" + direction
        #logger.info("Related object lookup: {}.".format(url))
        rsp = get_response(url)
        try:
            self.filter_root = ET.fromstring(rsp.text.encode('utf-8', 'ignore'))
        except ParseError:
            logger.error("Couldn't parse: {}".format(url))
            self.filter_root = None

    def __iter__(self):
        """
        For filter queries, run query with start stop params
        and yield an BaseEntity object with the Converis attributes.
        """
        if self.filter_root is None:
            return
        try:
            for grp in self.filter_root.findall('infoObject'):
                yield BaseEntity(root=grp, cid=grp.attrib['id'])
        except AttributeError:
            logger.error("Unable to parse related object: {}".format(self.url))
            


def filter_query(query, page_size=100):
    """
    Run filter query
    """
    start = 0
    stop = page_size
    while True:
        logger.debug("Fetching {} \n {} to {}.".format(query, start, stop))
        rsp = EntityFilter(query, start=start, stop=stop)
        if rsp.number <= stop:
            for x in rsp:
                yield x
            break
        else:
            start += page_size
            stop += page_size
            for x in rsp:
                yield x


def get_related_ids(entity_type, related_id, relationship, page_size=100):
    """
    Utility for fetching the ids of related entities.
    e.g. Publication, 1234, PUBL_has_CARD will get
    all publications related to card 1234

    Returns iterator
    """
    q = """
    <data xmlns="http://converis/ns/webservice">
      <return>
        <attributes>
        </attributes>
      </return>
      <query>
        <filter for="{}" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
        <and>
          <relation relatedto="{}" name="{}"/>
        </and>
        </filter>
      </query>
    </data>
    """
    query = q.format(entity_type, related_id, relationship)
    for ety in filter_query(query, page_size=page_size):
        yield ety.cid

def get_num_related_ids(entity_type, related_id, relationship, page_size=1):
    """
    Utility for fetching the ids of related entities.
    e.g. Publication, 1234, PUBL_has_CARD will get
    all publications related to card 1234

    Returns iterator
    """
    q = """
    <data xmlns="http://converis/ns/webservice">
      <return>
        <attributes>
        </attributes>
      </return>
      <query>
        <filter for="{}" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
        <and>
          <relation relatedto="{}" name="{}"/>
        </and>
        </filter>
      </query>
    </data>
    """
    query = q.format(entity_type, related_id, relationship)
    rsp = EntityFilter(query, start=0, stop=1)
    return rsp.number

def get_related_entities(entity_type, related_id, relationship, page_size=100):
    """
    Utility for fetching related entities.

    Returns iterator
    """
    q = """
    <data xmlns="http://converis/ns/webservice">
      <return>
      </return>
      <query>
        <filter for="{}" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
        <and>
          <relation relatedto="{}" name="{}"/>
        </and>
        </filter>
      </query>
    </data>
    """
    query = q.format(entity_type, related_id, relationship)
    for ety in filter_query(query, page_size=page_size):
        yield ety


def to_graph(cobj, mapped_class):
    """
    Utility taking an object representing a Converis
    entity and mapping it to a class with a method `to_rdf`
    that contains the necessary logic for creating VIVO mappings.

    returns: rdflib.graph
    """
    mc = mapped_class(**cobj.__dict__)
    return mc.to_rdf()


if __name__ == "__main__":
    print "hi"


