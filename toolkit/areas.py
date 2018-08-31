"""
Harvest areas
"""
from rdflib import Graph


from converis import client
import log_setup
import models
import utils

logger = log_setup.get_logger()

query = """
<data xmlns="http://converis/ns/webservice">
  <query>
    <filter for="Area"
      xmlns="http://converis/ns/filterengine"
      xmlns:sort="http://converis/ns/sortingengine">
      <and>
        <relation minCount="1" name="PERS_has_AREA"/>
      </and>
    </filter>
  </query>
</data>
"""


def harvest():
    g = Graph()
    for item in client.filter_query(query):
        g += client.to_graph(item, models.Expertise)
        break

    utils.serialize_g(g, "areas")


if __name__ == "__main__":
    logger.info("Starting area harvest.")
    harvest()
    logger.info("Harvest complete.")
