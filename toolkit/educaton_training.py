"""
Harvest education/training. 

"""
import csv
import os
import logging
import logging.handlers
import sys

from converis import backend
from converis import client
from converis.namespaces import D, VIVO, CONVERIS

# local models
import models
import log_setup

from utils import ThreadedHarvest

from rdflib import Graph, Literal

logger = log_setup.get_logger()

# use caching if enabled.
if os.environ.get('HTTP_CACHE') == "1":
  import requests_cache
  requests_cache.install_cache(
     'converis',
     backend='redis',
     allowable_methods=('GET', 'PUT'))

query = """
<data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="Education" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
        <or>
            <attribute argument="10368" name="dynamicType" operator="equals"/>
            <attribute argument="10370" name="dynamicType" operator="equals"/>
            <attribute argument="10369" name="dynamicType" operator="equals"/>
            <attribute argument="10371" name="dynamicType" operator="equals"/>
        </or>
      </filter>
     </query>
    </data>
"""

named_graph = "http://localhost/data/degrees"

def single_thread_harvest():
  g = Graph()
  for item in client.filter_query(query):
      g += client.to_graph(item, models.EducationTraining)
  backend.sync_updates(named_graph, g)


class EducationTrainingHarvest(ThreadedHarvest):

    def __init__(self, q, vmodel, threads=5):
        self.query = query
        self.graph = Graph()
        self.threads = threads
        self.vmodel = vmodel


def threaded_harvest():
    jh = EducationTrainingHarvest(query, models.EducationTraining)
    jh.run_harvest()
    logger.info("Harvest finished. Syncing to vstore.")
    jh.post_updates(named_graph)


if __name__ == "__main__":
    logger.info("Starting Education Training harvest.")
    #single_thread_harvest()
    threaded_harvest()
    logger.info("Education Training harvest finished.")
