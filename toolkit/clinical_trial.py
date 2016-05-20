"""
Primary harvest process.
"""

import os
import logging
import logging.handlers

from converis import backend
from converis import client
from converis.namespaces import D, VIVO, CONVERIS

# local models
import models
import log_setup

from rdflib import Graph, Literal

logger = log_setup.get_logger(client_level=logging.DEBUG)

if os.environ.get('HTTP_CACHE') == "1":
  import requests_cache
  requests_cache.install_cache(
     'converis',
     backend='redis',
     allowable_methods=('GET', 'PUT'))


def get_trials():
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
    for ct in ['5919557', '5920037', '6017368']:
      trial = client.Entity('ClinicalTrial', ct)
      g += client.to_graph(trial, models.ClinicalTrial)
    return g


def harvest():
    """
    """
    logger.info("Harvesting clinical trials.")
    g = get_trials()
    print g.serialize(format='n3')
    backend.sync_updates("http://localhost/data/trials", g)


if __name__ == "__main__":
    logger.info("Starting harvest.")
    harvest()