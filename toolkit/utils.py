import logging
import os
import sys
from Queue import Queue
from threading import Thread

from converis import client
from converis import backend

logger = logging.getLogger("harvest")

def chunk_pages(max, chunk_size=100):
    for x in range(1, max, chunk_size):
        yield (x, (x + chunk_size) - 1)


class ThreadedHarvest(object):
    page_size = 100

    def __init__(self, q, vmodel, threads=5):
        self.query = q
        self.graph = Graph()
        self.threads = threads
        logger.info("Threaded harvest of {}.".format(vmodel.__name__))
        self.vmodel = None

    def get_total(self):
        rsp = client.EntityFilter(self.query, start=0, stop=1)
        total = rsp.number
        logger.info("Total objects found: {}.".format(total))
        return total

    def get_pages(self):
        mx = self.get_total()
        out = []
        for start, stop in chunk_pages(mx, chunk_size=self.page_size):
            out.append((start, stop))
        return out


    def process(self, pair):
        start, stop = pair
        logging.info("Processing set {} to {}.".format(start, stop))
        rsp = client.EntityFilter(self.query, start=start, stop=stop)
        for ety in rsp:
            self.graph += client.to_graph(ety, self.vmodel)


    def harvest_service(self, num, harvest_q):
        """thread worker function"""
        while True:
            cid = harvest_q.get()
            logger.info('Worker: %s. Set: %s' % (num, cid))
            value = self.process(cid)
            harvest_q.task_done()
        return


    def run_harvest(self):
        num_fetch_threads = self.threads
        logging.info("Threaded harvest with {} threads.".format(self.threads))
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


    def post_updates(self, named_graph):
        if named_graph is None:
            raise Exception("No named graph provided")
        logger.info("Posting updates with {} triples.".format(len(self.graph)))
        backend.post_updates(named_graph, self.graph)

    def sync_updates(self, named_graph):
        if named_graph is None:
            raise Exception("No named graph provided")
        logger.info("Syncing updates with {} triples.".format(len(self.graph)))
        backend.sync_updates(named_graph, self.graph)
