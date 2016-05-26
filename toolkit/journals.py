import os
import logging
import logging.handlers

from converis import backend
from converis import client
from converis.namespaces import D, VIVO, CONVERIS

# local models
import models
import log_setup

from utils import ThreadedHarvest

from rdflib import Graph, Literal

logger = log_setup.get_logger()

if os.environ.get('HTTP_CACHE') == "1":
  import requests_cache
  requests_cache.install_cache(
     'converis',
     backend='redis',
     allowable_methods=('GET', 'PUT'))


journals_q = """
<data xmlns="http://converis/ns/webservice">
 <query>
  <filter for="Journal" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
  <and>
    <and>
     <relation minCount="1" name="PUBL_has_JOUR"/>
     <attribute argument="19.05.2016" name="Updated on" operator="greaterequal"/>
    </and>
  </and>
  </filter>
 </query>
</data>
"""

class JournalHarvest(ThreadedHarvest):

    def __init__(self, q, vmodel, threads=5):
        self.query = q
        self.graph = Graph()
        self.threads = threads
        self.vmodel = vmodel


def harvest():
    ng = "http://localhost/data/journals"
    jh = JournalHarvest(journals_q, models.Journal)
    jh.run_harvest()
    logger.info("Harvest finished. Syncing to vstore.")
    jh.post_updates(ng)


if __name__ == "__main__":
    logger.info("Starting harvest.")
    harvest()
