"""
Harvest orgs
"""
import os
import logging
import logging.handlers

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

# get orgs with cards or parent orgs that have child orgs with cards.
internal = """
<data xmlns="http://converis/ns/webservice">
 <query>
  <filter for="Organisation" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
   <or>
    <relation minCount="1" name="CARD_has_ORGA"/>
     <relation minCount="1" name="ORGA_has_child_ORGA">
       <relation minCount="1" name="CARD_has_ORGA"/>
     </relation>
     <relation minCount="1" name="EVEN_has_ORGA"/>
   </or>
  </filter>
 </query>
</data>
"""

class OrgaHarvest(ThreadedHarvest):

    def __init__(self, q, vmodel, threads=THREADS):
        self.query = q
        self.graph = Graph()
        self.threads = threads
        self.vmodel = vmodel
        #self.page_size = 30


def harvest():
    ng = "http://localhost/data/orgs"
    jh = OrgaHarvest(internal, models.Organization)
    jh.run_harvest()
    logger.info("Org harvest finished. Syncing to vstore.")
    jh.sync_updates(ng)


if __name__ == "__main__":
    logger.info("Starting harvest.")
    harvest()
