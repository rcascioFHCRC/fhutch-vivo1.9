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


def chunk_pages(max):
    chunk_size = 100
    for x in range(1, max, chunk_size):
        yield (x, (x + chunk_size) - 1)


class PositionsHarvest(object):

    def __init__(self, q, threads=5):
        self.query = q
        self.graph = Graph()
        self.threads = threads
        self.named_graph = "http://localhost/data/positions"

    def get_total(self):
        rsp = client.EntityFilter(self.query, start=0, stop=1)
        total = rsp.number
        logging.info("Total positions found: {}.".format(total))
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
            g = client.to_graph(pub, models.Position)
            self.graph += g
            del g


    def harvest_service(self, num, harvest_q):
        """thread worker function"""
        while True:
            cid = harvest_q.get()
            logger.info('Worker: %s position set: %s' % (num, cid))
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

query = """
<data xmlns="http://converis/ns/webservice">
<return>
</return>
 <query>
  <filter for="Card" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
    <!-- <or>
       <attribute operator="equals" argument="12167" name="positionType"/>
       <attribute operator="equals" argument="12169" name="positionType"/>
       <attribute operator="equals" argument="12172" name="positionType"/>
       <attribute operator="equals" argument="12170" name="positionType"/>
       <attribute operator="equals" argument="12173" name="positionType"/>
    </or> -->
    <and>
      <attribute operator="equals" argument="11288" name="currentPosition"/>
      <attribute operator="equals" argument="12006" name="typeOfCard"/>
      <attribute operator="notequals" argument="12171" name="positionType"/>
      <attribute operator="notequals" argument="12166" name="positionType"/>
      <attribute operator="notequals" argument="12168" name="positionType"/>
    </and>
  </filter>
 </query>
</data>
"""

def harvest(query, sync=False):
    ph = PositionsHarvest(query)
    #Threaded harvest
    ph.run_harvest()
    # Send the updates to VIVO
    if sync is True:
        ph.sync_updates()
    else:
        ph.post_updates()


if __name__ == "__main__":
    logger.info("Starting positions harvest.")
    harvest(query, sync=True)
