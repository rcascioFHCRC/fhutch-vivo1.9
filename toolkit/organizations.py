"""
Harvest orgs
"""

from rdflib import Graph
from rdflib.query import ResultException


from converis import client, backend
import log_setup
import models
import utils

logger = log_setup.get_logger()


NG = "http://localhost/data/orgs"
VNG = "http://localhost/data/orgs-videos"

# get orgs with cards or parent orgs that have child orgs with cards.
internal_orgs_query = """
<data xmlns="http://converis/ns/webservice">
 <query>
  <filter for="Organisation"
    xmlns="http://converis/ns/filterengine"
    xmlns:sort="http://converis/ns/sortingengine">
   <or>
    <relation minCount="1" name="CARD_has_ORGA"/>
     <relation minCount="1" name="ORGA_has_child_ORGA">
       <relation minCount="1" name="CARD_has_ORGA"/>
     </relation>
     <relation minCount="1" name="EVEN_has_ORGA"/>
     <relation minCount="1" name="EVEN_has_host_ORGA"/>
   </or>
  </filter>
 </query>
</data>
"""


def related_videos():
    """
    Get videos related to people with positions in this org.
    """
    q = models.rq_prefixes + """
    CONSTRUCT {
        ?org fhd:video ?video .
    }
    WHERE {
      ?p a foaf:Person ;
         fhd:video ?video .
       ?p vivo:relatedBy ?position .
      ?position a vivo:Position ;
                vivo:relates ?p, ?org .
      ?org a fhd:Organization .
    }
    """
    vstore = models.get_store()
    try:
        g = vstore.query(q)
        logger.info("Found {} org videos".format(len(g)))
    except ResultException:
        g = Graph()
    backend.sync_updates(VNG, g)


def harvest():
    g = Graph()
    for item in client.filter_query(internal_orgs_query):
        g += client.to_graph(item, models.Organization)

    utils.serialize_g(g, "orgs")


if __name__ == "__main__":
    logger.info("Starting harvest.")
    harvest()
