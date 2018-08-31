"""
Harvest pictures.

By default, this will harvest pictures updated since yesterday.

To harvest all pictures, run as:
$ python pictures all
"""

import base64
import os
import sys

from rdflib import Graph, Literal

from converis import client, backend
import log_setup
from models import FHD
from models import person_uri, org_uri, BaseModel
import utils

logger = log_setup.get_logger()

NG = "http://localhost/data/photos"

QUERY = """
<data xmlns="http://converis/ns/webservice">
  <query>
    <filter for="Person" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
    <and>
        <relation minCount="1" name="PERS_has_PICT">
            <attribute argument="2000-01-01" name="Updated on" operator="greaterequal"/>
        </relation>
    </and>
    </filter>
  </query>
</data>
"""

class PersonPicture(BaseModel):
    """
    For pictures, we will go from the person to the picture.
    This avoids data issues that we were seeing when attempting
    to harvest the picture entity directly.
    """

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
        # g = Graph()
        # related_entities = self.get_related_entities()
        # for uri in self.get_related_entities():
        #     url_base = os.environ['PHOTO_BASE_URL']
        #     fname = "{}.jpg".format(self.cid)
        #     full_path = os.path.join(os.environ['IMAGE_PATH'], fname)
        #     url = url_base + fname
        #     with open(full_path, 'wb') as of:
        #         dcd = base64.decodestring(self.filedata)
        #         of.write(dcd)
        #         g.add((uri, FHD.image, Literal(url)))
        #         break
        return self.picture()

    def picture(self):
        g = Graph()
        url_base = os.environ['PHOTO_BASE_URL']
        fname = "{}.jpg".format(self.cid)
        full_path = os.path.join(os.environ['IMAGE_PATH'], fname)
        url = url_base + fname
        puri = person_uri(self.cid)
        for item in client.RelatedObject('Person', self.cid, 'PERS_has_PICT'):
            with open(full_path, 'wb') as of:
                dcd = base64.decodestring(item.filedata)
                of.write(dcd)
                g.add((puri, FHD.image, Literal(url)))
                break
        return g


def harvest():
    """
    Fetch all pics and write to file
    """
    logger.info("Harvesting all pictures.")
    g = Graph()
    for per_pict in client.filter_query(QUERY):
        g += client.to_graph(per_pict, PersonPicture)
    logger.info("Picture harvest complete")
    if len(g) < 200:
        logger.error("Picture data incomplete. Not updating")
    else:
        backend.sync_updates(NG, g)


def harvest_updates(days=2, test=False):
    """
    Fetch updated pics and write to file.
    Default to days as 2 so that we get yesterday's date.
    """
    updated_date = utils.days_ago(days)
    logger.info("Harvesting updated pictures since {}.".format(updated_date))
    query = QUERY.replace("2000-01-01", updated_date)
    g = Graph()
    done = 0
    for pict in client.filter_query(query):
        g += client.to_graph(pict, PersonPicture)
        done += 1
        if test is True:
            if done > 10:
                break
    if len(g) > 0:
        utils.serialize_g(g, "photos")
        logger.info("Updated picture harvest complete. Updated: {}".format(done))
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
