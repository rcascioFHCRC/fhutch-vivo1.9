"""
Awards harvest process.
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

from utils import ThreadedHarvest

logger = log_setup.get_logger()

from models import (
  BaseModel,
  FHD,
  Resource,
  RDF,
  RDFS,
  person_uri,
  org_uri
)

if os.environ.get('HTTP_CACHE') == "1":
  import requests_cache
  requests_cache.install_cache(
     'converis',
     backend='redis',
     allowable_methods=('GET', 'PUT'))

NG = "http://localhost/data/awards"

query = """
<data xmlns="http://converis/ns/webservice">
 <query>
  <filter for="Award" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
  </filter>
 </query>
</data>
"""


class Award(BaseModel):

    def get_type(self, default=FHD.Award):
        """
        """
        return default

    def get_awardee(self):
        g = Graph()
        people = client.RelatedObject('Award', self.cid, 'PERS_has_AWRD')
        for person in people:
            puri = person_uri(person.cid)
            g.add((self.uri, VIVO.relates, puri))
        return g

    def get_awarded_by(self):
        #g = Graph()
        for org in client.get_related_entities('Organisation', self.cid, 'AWRD_has_ORGA'):
            #ouri = org_uri(org.cid)
            return org.cfname
            #g.add((self.uri, FHD.awardedBy, ouri))
        return None

    def add_date(self):
        g = Graph()
        on_date = self._v('awardedon')
        if on_date is not None:
            date_uri, dg = self._date("degree", on_date)
            g += dg
            g.add((self.uri, VIVO.dateTimeValue, date_uri))
        return g

    def build_label(self):
        lb = [self.nameofhonor]
        lb.append(self.get_awarded_by())
        label = ", ".join([l for l in lb if l is not None])
        return Literal(label)


    def to_rdf(self):
        g = Graph()
        r = Resource(g, self.uri)
        r.set(RDF.type, self.get_type())
        label = self.build_label()
        r.set(RDFS.label, Literal(label))
        r.set(CONVERIS.converisId, Literal(self.cid))

        if hasattr(self, 'url'):
            r.set(FHD.url, Literal(self.url))

        g += self.get_awardee()
        #g += self.get_awarded_by()
        g += self.add_date()

        return g


def single_thread_harvest_awards(sample=True):
    """
    Fetch all news items
    """
    logger.info("Harvesting Awards.")
    g = Graph()
    done = 0
    for award in client.filter_query(query):
        g += client.to_graph(award, Award)
        done += 1
        #if (sample is True) and (done >= 20):
        #    break
    print g.serialize(format='n3')
    backend.sync_updates(NG, g)


class AwardHarvest(ThreadedHarvest):

    def __init__(self, q, vmodel, threads=5):
        self.query = query
        self.graph = Graph()
        self.threads = threads
        self.vmodel = vmodel


def threaded_harvest():
    jh = AwardHarvest(query, Award)
    jh.run_harvest()
    logger.info("Harvest finished. Syncing to vstore.")
    jh.post_updates(NG)


if __name__ == "__main__":
    logger.info("Starting Award harvest.")
    single_thread_harvest_awards()
    #threaded_harvest()
    logger.info("Award harvest complete.")
