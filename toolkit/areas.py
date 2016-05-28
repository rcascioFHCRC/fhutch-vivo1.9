"""
Harvest areas
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


query = """
<data xmlns="http://converis/ns/webservice">
<query>
<filter for="Area" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
<relation minCount="1" name="PERS_has_AREA">
</relation>
</filter>
</query>
</data>
"""

class AreaHarvest(ThreadedHarvest):

    def __init__(self, q, vmodel, threads=3):
        self.query = q
        self.graph = Graph()
        self.threads = threads
        self.vmodel = vmodel


def harvest():
    ng = "http://localhost/data/areas"
    jh = AreaHarvest(query, models.Expertise)
    jh.run_harvest()
    logger.info("Harvest finished. Syncing to vstore.")
    jh.sync_updates(ng)


if __name__ == "__main__":
    logger.info("Starting area harvest.")
    harvest()
