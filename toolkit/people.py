"""
People harvest
"""
import logging
import os
import sys
from Queue import Queue
from threading import Thread

import logging
import logging.handlers

from converis import backend
from converis import client
from converis.namespaces import D, VIVO, CONVERIS

import xml.etree.ElementTree as ET

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


def add_since(time_stamp):
    dstring = time_stamp.strftime('%d.%m.%Y')
    df = ET.Element("attribute",
        {
        'operator': 'greaterequal',
        'argument': dstring,
        'name': "Updated on"
        }
    )
    return ET.tostring(df)



def chunk_pages(max):
    chunk_size = 100
    for x in range(1, max, chunk_size):
        yield (x, (x + chunk_size) - 1)


class PeopleHarvest(object):

    def __init__(self, q, threads=5):
        self.query = q
        self.graph = Graph()
        self.threads = threads
        self.named_graph = "http://localhost/data/people"

    def get_total(self):
        rsp = client.EntityFilter(self.query, start=0, stop=1)
        total = rsp.number
        logging.info("Total people found: {}.".format(total))
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
        for ety in rsp:
            g = client.to_graph(ety, models.Person)
            self.graph += g
            del g


    def harvest_service(self, num, harvest_q):
        """thread worker function"""
        while True:
            cid = harvest_q.get()
            logger.info('Worker: %s people set: %s' % (num, cid))
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
      <attributes>
       <attribute name="Short description"/>
       <attribute name="cfFamilyNames"/>
       <attribute name="cfFirstNames"/>
       <attribute name="middleName"/>
       <attribute name="email"/>
       <attribute name="ORCID"/>
       <attribute name="academicTitle"/>
       <attribute name="cfResInt"/>
      </attributes>
     </return>
     <query>
      <filter for="Person" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
       <and>
        <and>
         <attribute argument="12105" name="typeOfPerson" operator="equals"/>
        </and>
       </and>
      </filter>
     </query>
    </data>
"""

def harvest(query, sync=False):
    ph = PeopleHarvest(query)
    #Threaded harvest
    ph.run_harvest()
    sync = True
    # Send the updates to VIVO
    if sync is True:
        ph.sync_updates()
    else:
        ph.post_updates()


if __name__ == "__main__":
    logger.info("Starting people harvest.")
    harvest(query)

