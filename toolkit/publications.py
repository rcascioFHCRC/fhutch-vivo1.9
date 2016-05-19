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

from rdflib import Graph, Literal

logger = log_setup.get_logger(client_level=logging.DEBUG)


if os.environ.get('HTTP_CACHE') == "1":
    import requests_cache
    requests_cache.install_cache(
       'converis',
       backend='redis',
       allowable_methods=('GET', 'PUT'))

THREADS = int(os.environ.get('THREADS', 5))

def _p(msg):
    sys.stdout.write(msg + "\n")


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

    _p('*** Main thread waiting')
    harvest_queue.join()
    _p('*** Done')


def process_pub_card(card):
    """
    Process publication card relations.
    We should maybe just generate the authorship here too and eliminate the need
    for the post-ingest query.
    """
    logger.info("Fetching people and pubs for card {}.".format(card))
    g = Graph()
    # Relate pub to card
    for pub in client.get_related_ids('Publication', card, 'PUBL_has_CARD'):
        pub_uri = models.pub_uri(pub)
        g.add((pub_uri, CONVERIS.pubCardId, Literal(card)))
    # Relate card to pub
    for person in client.get_related_ids('Person', card, 'PERS_has_CARD'):
        puri = models.person_uri(person)
        g.add((puri, CONVERIS.pubCardId, Literal(card)))
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


def chunk_pages(max):
    chunk_size = 100
    for x in range(1, max, chunk_size):
        yield (x, (x + chunk_size) - 1)


class PubHarvest(object):

    def __init__(self, q, threads=5):
        self.query = q
        self.graph = Graph()
        self.threads = threads
        self.named_graph = "http://localhost/data/publications"

    def get_total(self):
        rsp = client.EntityFilter(self.query, start=0, stop=1)
        total = rsp.number
        logging.info("Total pubs found: {}.".format(total))
        return total

    def get_pages(self):
        mx = self.get_total()
        out = []
        for start, stop in chunk_pages(mx):
            out.append((start, stop))
        return out


    def process(self, pair):
        start, stop = pair
        #_p("Processing {} {}".format(start, stop))
        #self.total += 1
        rsp = client.EntityFilter(self.query, start=start, stop=stop)
        for pub in rsp:
            g = client.to_graph(pub, models.Publication)
            self.graph += g
            del g


    def harvest_service(self, num, harvest_q):
        """thread worker function"""
        while True:
            cid = harvest_q.get()
            logger.info('Worker: %s pub set: %s' % (num, cid))
            value = self.process(cid)
            harvest_q.task_done()
        return


    def run_harvest(self):
        num_fetch_threads = self.threads
        harvest_queue = Queue()
        # Set up some threads to fetch the enclosures
        for i in range(num_fetch_threads):
            worker = Thread(target=self.harvest_service, args=(i, harvest_queue,))
            worker.setDaemon(True)
            worker.start()

        pages = self.get_pages()
        for st_sp in pages:
            harvest_queue.put(st_sp)

        logger.debug('Harvest initialized')
        harvest_queue.join()
        logger.info("Threads complete.")


    def post_updates(self):
        logger.info("Posting updates with {} triples.".format(len(self.graph)))
        backend.post_updates(self.named_graph, self.graph)

    def sync_updates(self):
        logger.info("Syncing updates with {} triples.".format(len(self.graph)))
        backend.sync_updates(self.named_graph, self.graph)


def pub_harvest(query, sync=False):
    ph = PubHarvest(query)
    #Threaded harvest
    ph.run_harvest()
    # Send the updates to VIVO
    if sync is True:
        ph.sync_updates()
    else:
        ph.post_updates()


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


if __name__ == "__main__":
    #pub_harvest(all_pubs)
    harvest_sets()

    logger.info("Starting publications relations harvest.")

    # get pub cards
    cards = get_pub_cards()
    run_pub_card_harvest(cards)

    # Make authorships using card ids.
    generate_authorships()
