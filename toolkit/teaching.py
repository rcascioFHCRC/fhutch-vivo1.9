"""
Service harvest process.
"""
import os
import logging
import logging.handlers

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


service_q = """
<data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="TeachingAndLect" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
      </filter>
     </query>
    </data>
"""

class ServiceHarvest(ThreadedHarvest):

    def __init__(self, q, vmodel, threads=THREADS):
        self.query = q
        self.graph = Graph()
        self.threads = threads
        self.vmodel = vmodel
        #self.page_size = 30


def harvest():
    ng = "http://localhost/data/teaching"
    jh = ServiceHarvest(service_q, models.TeachingLecture)
    jh.run_harvest()
    logger.info("Service harvest finished. Syncing to vstore.")
    jh.sync_updates(ng)

if __name__ == "__main__":
    logger.info("Starting harvest.")
    harvest()
    #harvest_service(sample=False)
