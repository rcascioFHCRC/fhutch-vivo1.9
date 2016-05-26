"""
Threaded fetch of publications going from publication card
to pubs. E.g. /Card/1235/PUBL_has_CARD.
"""
import logging
import os
import sys
from Queue import Queue
from threading import Thread

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

THREADS = int(os.environ.get('THREADS', 5))

def harvest_sets():
    pq = """
    <data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="Publication" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
      <and>
        <and>
         <relation minCount="1" name="PUBL_has_CARD"/>
        </and>
        <and>
         <attribute argument="{stop}" name="publYear" operator="lessequal"/>
         <attribute argument="{start}" name="publYear" operator="greater"/>
        </and>
      </and>
      </filter>
     </query>
    </data>
    """
    #ps = [(1940, 1985), (1985, 1995), (1995, 2000), (2000, 2005), (2005, 2010), (2010, 2012), (2012, 2014), (2014, 2016)]
    ps = [(2005, 2010), (2010, 2016)]
    for start, stop in ps:
        logger.info("Harvesting pubs from {} to {}".format(start, stop))
        query = pq.format(**dict(start=start, stop=stop))
        pub_harvest(query)


def harvest_service(num, harvest_q):
    """thread worker function"""
    while True:
        cid = harvest_q.get()
        logger.info('Worker: %s card: %s' % (num, cid))
        process_pub_card(cid)
        harvest_q.task_done()
    return


def run_pub_card_harvest(to_fetch):
    num_fetch_threads = THREADS
    harvest_queue = Queue()
    # Set up some threads to fetch the enclosures
    for i in range(num_fetch_threads):
        worker = Thread(target=harvest_service, args=(i, harvest_queue,))
        worker.setDaemon(True)
        worker.start()

    for card in to_fetch:
        harvest_queue.put(card)

    harvest_queue.join()
    logger.info("Harvest complete")

def process_pub_card(card):
    """
    Process publication card relations.
    We should maybe just generate the authorship here too and eliminate the need
    for the post-ingest query.
    """
    logger.info("Fetching pubs for card {}.".format(card))
    g = Graph()
    # Relate pub to card
    for pub in client.get_related_entities('Publication', card, 'PUBL_has_CARD'):
        pub_uri = models.pub_uri(pub.cid)
        g.add((pub_uri, CONVERIS.pubCardId, Literal(card)))
        g += client.to_graph(pub, models.Publication)
    backend.sync_updates("http://localhost/data/pubs-card-{}".format(card), g)
    return


def generate_authorships():
    """
    Run SPARQL query to generate authorships by joining
    on converis:pubCardId.
    """
    logger.info("Generating authorships.")
    g = models.create_authorships()
    backend.sync_updates("http://localhost/data/authorship", g)


def get_pub_cards(sample=False):
    logger.info("Getting publications cards.")
    done = 0
    out = []
    for card in models.get_pub_cards():
        done += 1
        if sample is True:
            if done >= 100:
                break
        out.append(card)
    return out


class PubHarvest(ThreadedHarvest):

    def __init__(self, q, vmodel, threads=5):
        self.query = q
        self.vmodel = vmodel
        self.graph = Graph()
        self.threads = threads

def pub_harvest(query):
    ng = "http://localhost/data/publications"
    ph = PubHarvest(query, models.Publication)
    #Threaded harvest
    ph.run_harvest()
    logger.info("Harvest finished. Syncing to vstore.")
    # Send the updates to VIVO
    ph.post_updates(ng)




if __name__ == "__main__":
    logger.info("Starting publications relations harvest.")
    # get pub cards
    cards = get_pub_cards()
    run_pub_card_harvest(cards)
    # Make authorships using card ids.
    generate_authorships()
