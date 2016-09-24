"""
Clinical trials from file for now..
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

if os.environ.get('HTTP_CACHE') == "1":
  import requests_cache
  requests_cache.install_cache(
     'converis',
     backend='redis',
     allowable_methods=('GET', 'PUT'))


def get_trials(trials):
    q = """
    <data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="ClincialTrial" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
      </filter>
     </query>
    </data>
    """
    g = Graph()
    # pub = client.Entity('Publication', '2013874')
    # g += client.to_graph(pub, models.Publication)
    # org = client.Entity('Organisation', '148339')
    # g += client.to_graph(org, models.Organization)
    #for done, trial in enumerate(client.filter_query(q)):
    for ct in trials:
      trial = client.Entity('ClinicalTrial', ct)
      g += client.to_graph(trial, models.ClinicalTrial)
    return g


def harvest(trials):
    """
    """
    logger.info("Harvesting clinical trials.")
    g = get_trials(trials)
    #print g.serialize(format='n3')
    backend.sync_updates("http://localhost/data/trials", g)


query = """
<data xmlns="http://converis/ns/webservice">
  <return>
  </return>
  <query>
    <filter for="ClinicalTrial" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
     
    </filter>
  </query>
</data>
"""

class ClinicalTrialHarvest(ThreadedHarvest):

    def __init__(self, q, vmodel, threads=2):
        self.query = query
        self.graph = Graph()
        self.threads = threads
        self.vmodel = vmodel


ng = "http://localhost/data/trials"

def threaded_harvest():
    jh = ClinicalTrialHarvest(query, models.ClinicalTrial)
    jh.run_harvest()
    logger.info("Harvest finished. Syncing to vstore.")
    jh.sync_updates(ng)


def single_thread_harvest():
  g = Graph()
  for item in client.filter_query(query):
      g += client.to_graph(item, models.ClinicalTrial)
      #print item.cid, item.name
  #print>>sys.stderr, "adding triples", len(g)
  backend.sync_updates(ng, g)

if __name__ == "__main__":
    logger.info("Starting Cinical Trial harvest.")
    #single_thread_harvest()
    threaded_harvest()
    logger.info("Clinical trial harvest finished.")
