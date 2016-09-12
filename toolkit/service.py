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



def harvest_service(sample=False):
    """
    Fetch all news items
    """
    logger.info("Harvesting Service.")
    q = """
    <data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="Service" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
      </filter>
     </query>
    </data>
    """
    g = Graph()
    done = 0
    for item in client.filter_query(q):
        #print item.cid
        g += client.to_graph(item, models.Service)
        done += 1
        if (sample is True) and (done >= 100):
            break
    print g.serialize(format='n3')
    #backend.sync_updates("http://localhost/data/service", g)

service_q = """
<data xmlns="http://converis/ns/webservice">
 <query>
  <filter for="Service" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
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
    ng = "http://localhost/data/service"
    jh = ServiceHarvest(service_q, models.Service)
    jh.run_harvest()
    logger.info("Service harvest finished. Syncing to vstore.")
    jh.sync_updates(ng)

if __name__ == "__main__":
    logger.info("Starting harvest.")
    harvest()
    #harvest_service(sample=False)
