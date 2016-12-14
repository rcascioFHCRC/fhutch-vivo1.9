"""
Harvest pictures.

By default, this will harvest pictures updated since yesterday.

To harvest all pictures, run as:
$ python pictures all
"""

import base64
import csv
import os
import sys

from rdflib import Graph, Literal

from converis import client, backend
import log_setup

from models import FHD
from models import person_uri, BaseModel

from utils import days_ago

logger = log_setup.get_logger()

NG = "http://localhost/data/photos"

QUERY = """
<data xmlns="http://converis/ns/webservice">
  <query>
    <filter for="Picture" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
    <or>
        <relation minCount="1" name="PERS_has_PICT">
          <attribute argument="6019159" name="fhPersonType" operator="equals"/>
        </relation>
    </or>
    <and>
        <attribute argument="2000-01-01" name="Updated on" operator="greaterequal"/>
    </and>
    </filter>
  </query>
</data>
"""

class Picture(BaseModel):

    def get_related_entities(self):
        uris = []
        for person in client.get_related_ids('Person', self.cid, 'PERS_has_PICT'):
            puri = person_uri(person)
            uris.append(puri)

        for org in client.get_related_ids('Organisation', self.cid, 'ORGA_has_PICT'):
            ouri = org_uri(org)
            uris.append(ouri)

        return uris

    def to_rdf(self):
        g = Graph()
        related_entities = self.get_related_entities()
        for uri in self.get_related_entities():
            url_base = os.environ['PHOTO_BASE_URL']
            fname = "{}.jpg".format(self.cid)
            full_path = os.path.join(os.environ['IMAGE_PATH'], fname)
            url = url_base + fname
            with open(full_path, 'wb') as of:
                dcd = base64.decodestring(self.filedata)
                of.write(dcd)
                g.add((uri, FHD.image, Literal(url)))
                break
        return g


def harvest():
    """
    Fetch all pics and write to file
    """
    logger.info("Harvesting all pictures.")
    g = Graph()
    for pict in client.filter_query(QUERY):
        g += client.to_graph(pict, Picture)
    logger.info("Picture harvest complete")
    backend.sync_updates(NG, g)


def harvest_updates(days=2, test=False):
    """
    Fetch updated pics and write to file.
    Default to days as 2 so that we get yesterday's date.
    """
    updated_date = days_ago(days)
    logger.info("Harvesting updated pictures since {}.".format(updated_date))
    query = QUERY.replace("2000-01-01", updated_date)
    g = Graph()
    done = 0
    for pict in client.filter_query(query):
        g += client.to_graph(pict, Picture)
        done += 1
        if test is True:
            if done > 10:
                break
    if len(g) > 0:
        backend.post_updates(NG, g)
        logger.info("Updated picture harvest complete.")
    else:
        logger.info("No updated pictures found.")


if __name__ == "__main__":
    try:
        update = sys.argv[1]
    except IndexError:
        update = False
    if update == "all":
        harvest()
    else:
        harvest_updates()