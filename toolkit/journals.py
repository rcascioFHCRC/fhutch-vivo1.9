"""
Harvest journals.
"""

from rdflib import Graph

from converis import client
import models
import log_setup
import utils

logger = log_setup.get_logger()


journals_q = """
<data xmlns="http://converis/ns/webservice">
 <query>
  <filter for="Journal"
    xmlns="http://converis/ns/filterengine"
    xmlns:sort="http://converis/ns/sortingengine">
  <and>
    <and>
     <relation minCount="1" name="PUBL_has_JOUR"/>
     <!--<attribute argument="19.05.2016" name="Updated on" operator="greaterequal"/>-->
    </and>
  </and>
  </filter>
 </query>
</data>
"""


def harvest():
    g = Graph()
    for item in client.filter_query(journals_q):
        g += client.to_graph(item, models.Journal)
        break

    utils.serialize_g(g, "journals")


if __name__ == "__main__":
    logger.info("Starting harvest.")
    harvest()
