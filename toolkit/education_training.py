"""
Harvest education/training.

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
  <filter for="Education"
    xmlns="http://converis/ns/filterengine"
    xmlns:sort="http://converis/ns/sortingengine">
    <relation minCount="1" name="EDUC_has_PERS">
      <attribute argument="6019159" name="fhPersonType" operator="equals"/>
    </relation>
  </filter>
 </query>
</data>
"""


def harvest():
    g = Graph()
    for item in client.filter_query(query):
        g += client.to_graph(item, models.EducationTraining)

    utils.serialize_g(g, "degrees")


if __name__ == "__main__":
    logger.info("Starting Education Training harvest.")
    harvest()
    logger.info("Education Training harvest finished.")
