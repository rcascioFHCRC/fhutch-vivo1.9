"""
Threaded fetch of publications.
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
from rdflib.namespace import RDF

logger = log_setup.get_logger()


if os.environ.get('HTTP_CACHE') == "1":
    import requests_cache
    requests_cache.install_cache(
       'converis',
       backend='redis',
       allowable_methods=('GET', 'PUT'))

THREADS = int(os.environ.get('THREADS', 5))

NG = "http://localhost/data/publications"

QUERY = """
<data xmlns="http://converis/ns/webservice">
    <query>
        <filter for="Publication" xmlns="http://converis/ns/filterengine" xmlns:ns2="http://converis/ns/sortingengine">
        <and>
            <or>
                <relation direction="lefttoright" name="PUBL_has_CARD">
                    <relation direction="righttoleft"  name="PERS_has_CARD">
                        <attribute argument="6019159" name="fhPersonType" operator="equals"/>
                    </relation>
                </relation>
                <relation direction="lefttoright" name="PUBL_has_editor_CARD">
                    <relation direction="righttoleft"  name="PERS_has_CARD">
                        <attribute argument="6019159" name="fhPersonType" operator="equals"/>
                    </relation>
                </relation>
            </or>
        </and>
        </filter>
    </query>
</data>
"""

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


def generate_local_coauthor():
    """
    Run SPARQL query to generate a boolean indicating that
    the person has a local coauthor.
    """
    logger.info("Generating local coauthor flag.")
    g = models.create_local_coauthor_flag()
    backend.sync_updates("http://localhost/data/local-coauthors", g)

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


def pub_harvest():
    q = """
    <data xmlns="http://converis/ns/webservice">
    <query>
    <filter for="Publication" xmlns="http://converis/ns/filterengine" xmlns:ns2="http://converis/ns/sortingengine">
    <and>
        <and>
            <relation direction="lefttoright" name="PUBL_has_CARD">
                <relation direction="righttoleft"  name="PERS_has_CARD">
                    <attribute argument="6019159" name="fhPersonType" operator="equals"/>
                </relation>
            </relation>
        </and>
    </and>
    </filter>
    </query>
    </data>
    """
    g = Graph()
    for item in client.filter_query(q):
        g += client.to_graph(item, models.Publication)
    ng = "http://localhost/data/publications"
    backend.sync_updates(ng, g)


def threaded_pub_harvest():
    ph = PubHarvest(QUERY, models.Publication)
    ph.run_harvest()
    logger.info("Publications harvest finished. Syncing to vstore")
    ph.sync_updates(NG)


def generate_authorships():
    """
    Run SPARQL query to generate authorships by joining
    on converis:pubCardId.
    """
    g = Graph()
    for person_uri, card_id in models.get_pub_cards():
        for pub in client.get_related_ids('Publication', card_id, 'PUBL_has_CARD'):
            pub_uri = models.pub_uri(pub)
            uri = models.hash_uri("authorship", person_uri.toPython() + pub_uri.toPython())
            g.add((uri, RDF.type, VIVO.Authorship))
            g.add((uri, VIVO.relates, person_uri))
            g.add((uri, VIVO.relates, pub_uri))
    backend.sync_updates("http://localhost/data/authorship", g)


def clear_pub_cards():
    """
    Delete all the pubs-cards named graphs.
    """
    # get pub cards
    cards = get_pub_cards()
    for card_uri, card in cards:
        g = Graph()
        backend.sync_updates("http://localhost/data/pubs-card-{}".format(card), g)


def sample_harvest():
    q = """
    <data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="Publication" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
        <attribute operator="equals" argument="10347" name="Publication type"/>
      </filter>
     </query>
    </data>
    """
    logger.info("Starting sample publications harvest.")
    g = Graph()
    for item in client.filter_query(q):
        g += client.to_graph(item, models.Publication)
    # print g.serialize(format="turtle")
    # backend.sync_updates replaces the named graph with the incoming data - meaning any
    # data in the system that's not in the incoming data will be deleted
    # backend.post_updates will only update the entities that are in the incoming data - anything
    # else is left as it is.
    backend.sync_updates("http://localhost/data/sample-books", g)


def generate_orgs_to_pubs():
    """
    Relate pubs to orgs through publication cards.
    """
    g = Graph()
    for person_uri, card_id in models.get_pub_cards():
        for org in client.get_related_entities('Organisation', card_id, 'CARD_has_ORGA'):
            if org.intorext['value'] == 'internal':
                ouri = models.org_uri(org.cid)
                for pub in client.get_related_ids('Publication', card_id, 'PUBL_has_CARD'):
                    pub_uri = models.pub_uri(pub)
                    print "card", card_id, "org", org.cid, "pub", pub
                    g.add((ouri, VIVO.relates, pub_uri))
    backend.sync_updates("http://localhost/data/org-pubs", g)


def full_publication_harvest():
    logger.info("Starting publications harvest.")
    threaded_pub_harvest()
    logger.info("Generating authorships")
    generate_authorships()
    logger.info("Adding local coauthor flag.")
    generate_local_coauthor()
    logger.info("Pub harvest and authorship generation complete.")
    logger.info("Relating orgs to publications.")
    generate_orgs_to_pubs()


if __name__ == "__main__":
    #sample_harvest()
    full_publication_harvest()
    #generate_orgs_to_pubs()
