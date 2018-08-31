"""
Teaching harvest process.
"""
import os
import logging
import logging.handlers

from converis import backend
from converis import client

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

NG = "http://localhost/data/teaching"

query = """
<data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="TeachingAndLect" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
      </filter>
     </query>
    </data>
"""

class TeachingHarvest(ThreadedHarvest):

    def __init__(self, q, vmodel, threads=THREADS):
        self.query = q
        self.graph = Graph()
        self.threads = threads
        self.vmodel = vmodel
        #self.page_size = 30


def harvest():
    jh = TeachingHarvest(query, models.TeachingLecture)
    jh.run_harvest()
    logger.info("Service harvest finished. Syncing to vstore.")
    jh.sync_updates(NG)



def single_thread_harvest():
    """
    Fetch all news items
    """
    logger.info("Harvesting Teaching.")
    g = Graph()
    done = 0
    for award in client.filter_query(query):
        g += client.to_graph(award, models.TeachingLecture)
        done += 1
        #if (done >= 20):
        #    break
    print g.serialize(format='turtle')
    backend.sync_updates(NG, g)


if __name__ == "__main__":
    logger.info("Starting teaching harvest.")
    harvest()
    #single_thread_harvest()
    logger.info("Teaching harvest complete.")
