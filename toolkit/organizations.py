"""
Harvest orgs
"""
import os
import logging
import logging.handlers

from rdflib.query import ResultException

from converis import client, backend

# local models
import models
import log_setup

from utils import ThreadedHarvest

from rdflib import Graph

logger = log_setup.get_logger()

if os.environ.get('HTTP_CACHE') == "1":
  import requests_cache
  requests_cache.install_cache(
     'converis',
     backend='redis',
     allowable_methods=('GET', 'PUT'))

THREADS = int(os.environ['THREADS'])

NG = "http://localhost/data/orgs"
VNG = "http://localhost/data/orgs-videos"

# get orgs with cards or parent orgs that have child orgs with cards.
internal_orgs_query = """
<data xmlns="http://converis/ns/webservice">
 <query>
  <filter for="Organisation" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
   <or>
    <relation minCount="1" name="CARD_has_ORGA"/>
     <relation minCount="1" name="ORGA_has_child_ORGA">
       <relation minCount="1" name="CARD_has_ORGA"/>
     </relation>
     <relation minCount="1" name="EVEN_has_ORGA"/>
     <relation minCount="1" name="EVEN_has_host_ORGA"/>
   </or>
  </filter>
 </query>
</data>
"""

class OrgaHarvest(ThreadedHarvest):

    def __init__(self, q, vmodel, threads=THREADS):
        self.query = internal_orgs_query
        self.graph = Graph()
        self.threads = threads
        self.vmodel = vmodel
        #self.page_size = 30


def related_videos():
    """
    Get videos related to people with positions in this org.
    """
    q = models.rq_prefixes + """
    CONSTRUCT {
        ?org fhd:video ?video .
    }
    WHERE {
      ?p a foaf:Person ;
         fhd:video ?video .
       ?p vivo:relatedBy ?position .
      ?position a vivo:Position ;
                vivo:relates ?p, ?org .
      ?org a fhd:Organization .
    }
    """
    vstore = models.get_store()
    try:
        g = vstore.query(q)
        logger.info("Found {} org videos".format(len(g)))
    except ResultException:
        g = Graph()
    backend.sync_updates(VNG, g)

def harvest():
    jh = OrgaHarvest(internal_orgs_query, models.Organization)
    jh.run_harvest()
    logger.info("Org harvest finished. Syncing to vstore.")
    jh.sync_updates(NG)


def single_thread_harvest():
    g = Graph()
    for item in client.filter_query(internal_orgs_query):
        g += client.to_graph(item, models.Organization)
    backend.sync_updates(NG, g)


if __name__ == "__main__":
    logger.info("Starting harvest.")
    harvest()
    #single_thread_harvest()
    #related_videos()
