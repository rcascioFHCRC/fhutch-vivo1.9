"""
People harvest
"""
import logging
import os
import pickle
import sys
from Queue import Queue
from threading import Thread

import logging
import logging.handlers

from converis import backend
from converis import client
from converis.namespaces import D, VIVO, CONVERIS

import xml.etree.ElementTree as ET

# local models
import models
import log_setup

from rdflib import Graph, Literal

from utils import ThreadedHarvest


logger = log_setup.get_logger()

if os.environ.get('HTTP_CACHE') == "1":
  import requests_cache
  requests_cache.install_cache(
     'converis',
     backend='redis',
     allowable_methods=('GET', 'PUT'))


def add_since(time_stamp):
    dstring = time_stamp.strftime('%d.%m.%Y')
    df = ET.Element("attribute",
        {
        'operator': 'greaterequal',
        'argument': dstring,
        'name': "Updated on"
        }
    )
    return ET.tostring(df)

query = """
    <data xmlns="http://converis/ns/webservice">
     <return>
      <attributes/>
     </return>
     <query>
      <filter for="Person" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
      </filter>
     </query>
    </data>
"""

class PersonHarvest(ThreadedHarvest):

    def __init__(self, q, vmodel, threads=5):
        self.query = q
        self.graph = Graph()
        self.threads = threads
        self.vmodel = vmodel

    def process(self, pair):
        start, stop = pair
        #_p("Processing {} {}".format(start, stop))
        #self.total += 1
        rsp = client.EntityFilter(self.query, start=start, stop=stop)
        for ety in rsp:
            item = client.Entity('Person', ety.cid)
            # FH people only
            if hasattr(item, 'fhpersontype'):
                if item.fhpersontype['cid'] == '6019159':
                    g = client.to_graph(item, models.Person)
                    self.graph += g


def harvest():
    ng = "http://localhost/data/people"
    ph = PersonHarvest(query, models.Person)
    ph.run_harvest()
    logger.info("Harvest finished. Syncing to vstore.")
    ph.sync_updates(ng)


def build_short_url_index():
    query = """
    <data xmlns="http://converis/ns/webservice">
     <return>
      <attributes>
        <attribute name="shortURL"/>
       </attributes>
     </return>
     <query>
      <filter for="Person" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
        <and>
          <attribute operator="notequals" argument="" name="shortURL"/>
        </and>
      </filter>
     </query>
    </data>
    """
    d = {}
    for item in client.filter_query(query):
        d[item.cid] = item.shorturl
    with open('data/people.idx', 'wb') as of:
        pickle.dump(d, of)



if __name__ == "__main__":
    build_short_url_index()
    logger.info("Starting people harvest.")
    harvest()

