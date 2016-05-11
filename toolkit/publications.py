"""
Threaded fetch of publications going from publication card
to pubs. E.g. /Card/1235/PUBL_has_CARD.
"""
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

from rdflib import Graph, Literal

logger = log_setup.get_logger()


if os.environ.get('HTTP_CACHE') == "1":
    import requests_cache
    requests_cache.install_cache(
       'converis',
       backend='redis',
       allowable_methods=('GET', 'PUT'))

THREADS = int(os.environ.get('THREADS', 3))

def _p(msg):
    sys.stdout.write(msg + "\n")


def harvest_service(num, harvest_q):
    """thread worker function"""
    while True:
        cid = harvest_q.get()
        logging.info('Worker: %s card: %s' % (num, cid))
        process_pub_card(cid)
        harvest_q.task_done()
    return


def run_harvest(to_fetch):
    num_fetch_threads = THREADS
    harvest_queue = Queue()
    # Set up some threads to fetch the enclosures
    for i in range(num_fetch_threads):
        worker = Thread(target=harvest_service, args=(i, harvest_queue,))
        worker.setDaemon(True)
        worker.start()

    for card in to_fetch:
        harvest_queue.put(card)

    _p('*** Main thread waiting')
    harvest_queue.join()
    _p('*** Done')


def process_pub_card(cid):
    logging.info("Fetching pubs for card {}.".format(cid))
    g = Graph()
    for pub in client.RelatedObject('Card', cid, 'PUBL_has_CARD'):
        pg = client.to_graph(pub, models.Publication)
        pub_uri = models.pub_uri(pub.cid)
        g += pg
        del pg
        g.add((pub_uri, CONVERIS.pubCardId, Literal(cid)))
    #print g.serialize(format='turtle')
    backend.sync_updates("http://localhost/data/pubs-card-{}".format(cid), g)
    #backend.post_updates("http://localhost/data/pubs", g)

def generate_authorships():
    """
    Run SPARQL query to generate authorships by joining
    on converis:pubCardId.
    """
    logger.info("Generating authorships.")
    g = models.create_authorships()
    backend.sync_updates("http://localhost/data/authorship", g)


def get_pub_cards(sample=False):
    q = """
    <data xmlns="http://converis/ns/webservice">
    <return>
    <attributes/>
    </return>
     <query>
      <filter for="Card" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
        <and>
          <relation name="PUBL_has_CARD" minCount="1"/>
          <!-- <attribute operator="equals" argument="12166" name="positionType"/> -->
        </and>
      </filter>
     </query>
    </data>
    """
    logger.info("Getting publications cards.")
    g = Graph()
    done = 0
    out = []
    for card in client.filter_query(q):
        done += 1
        if sample is True:
            if done >= 100:
                break
        out.append(card.cid)
    return out

if __name__ == "__main__":
    logger.info("Starting publications harvest.")
    # cards = get_pub_cards()
    # run_harvest(cards)
    # generate_authorships()
    client.make_error()
