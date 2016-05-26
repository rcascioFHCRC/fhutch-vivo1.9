"""
News harvest process.
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



def harvest_news(sample=False):
    """
    Fetch all news items
    """
    logger.info("Harvesting News.")
    q = """
    <data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="News" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
      </filter>
     </query>
    </data>
    """
    g = Graph()
    done = 0
    for news in client.filter_query(q):
        g += client.to_graph(news, models.News)
        done += 1
        if (sample is True) and (done >= 20):
            break
    #print g.serialize(format='n3')
    backend.sync_updates("http://localhost/data/news", g)


if __name__ == "__main__":
    logger.info("Starting harvest.")
    harvest_news(sample=True)
