"""

Harvest orgs that are related to other entities we are tracking.

This doesn't include cards/positions, which are handled by organizations.py.

This prevents duplicating org data in several different named graphs.
"""
from rdflib import Graph

import log_setup
import models
import utils

from converis import client


logger = log_setup.get_logger()

internal = """
<data xmlns="http://converis/ns/webservice">
 <query>
  <filter for="Organisation" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
   <or>
    <!--
    <relation minCount="1" name="LECT_has_ORGA"/>
    <relation minCount="1" name="AWRD_has_ORGA"/>
    <relation minCount="1" name="EDUC_has_ORGA"/>
    <relation minCount="1" name="SERV_has_ORGA"/> -->
    <relation minCount="1" name="CLIN_has_ORGA"/>
   </or>
  </filter>
 </query>
</data>
"""


def harvest():
    g = Graph()
    for item in client.filter_query(internal):
        g += client.to_graph(item, models.RelatedOrganization)
    utils.serialize_g(g, "related-orgs")


if __name__ == "__main__":
    logger.info("Starting harvest.")
    harvest()
