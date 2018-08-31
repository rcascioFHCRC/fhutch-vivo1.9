"""
People harvest
"""
import xml.etree.ElementTree as ET

from rdflib import Graph

from converis import client
import models
import log_setup
import utils

logger = log_setup.get_logger()


def add_since(time_stamp):
    dstring = time_stamp.strftime('%d.%m.%Y')
    df = ET.Element("attribute", {
            'operator': 'greaterequal',
            'argument': dstring,
            'name': "Updated on"
        }
    )
    return ET.tostring(df)


query = """
    <data xmlns="http://converis/ns/webservice">
     <return>
      <attributes/>
     </return>
     <query>
      <filter for="Person"
        xmlns="http://converis/ns/filterengine"
        xmlns:sort="http://converis/ns/sortingengine">
      </filter>
     </query>
    </data>
"""


def harvest():
    g = Graph()
    for ety in client.filter_query(query):
        item = client.Entity('Person', ety.cid)
        # FH people only
        if hasattr(item, 'fhpersontype'):
            if item.fhpersontype['cid'] == '6019159':
                g += client.to_graph(item, models.Person)
                logger.debug("Found person {}.".format(item.cid))

    utils.serialize_g(g, "people")


if __name__ == "__main__":
    logger.info("Starting people harvest.")
    harvest()
