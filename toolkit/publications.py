import logging
import logging.handlers
import sys
from Queue import Queue
from threading import Thread

from converis import backend
from converis import client
from converis.namespaces import D, VIVO, CONVERIS

# local models
import models

from rdflib import Graph, Literal

import requests_cache
requests_cache.install_cache(
    'converis',
    backend='redis',
    allowable_methods=('GET', 'PUT'))

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
)

# Set up a specific logger with our desired output level
logger = logging.getLogger("converis_client")
logger.setLevel(logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

THREADS = 2

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
        pub_uri, pg = client.to_graph2(pub, models.Publication)
        g += pg
        del pg
        g.add((pub_uri, CONVERIS.pubCardId, Literal(cid)))
    #print g.serialize(format='turtle')
    backend.sync_updates("http://localhost/data/pubs-card-{}".format(cid), g)


def get_pub_cards():
    q = """
    <data xmlns="http://converis/ns/webservice">
    <return>
    <attributes/>
    </return>
     <query>
      <filter for="Card" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
        <and>
          <relation name="PUBL_has_CARD" minCount="1"/>
          <attribute operator="equals" argument="12166" name="positionType"/>
        </and>
      </filter>
     </query>
    </data>
    """
    g = Graph()
    done = 0
    out = []
    for card in client.filter_query(q):
        done += 1
        if done >= 100:
            break
        out.append(card.cid)
    return out

if __name__ == "__main__":
    cards = get_pub_cards()
    run_harvest(cards)