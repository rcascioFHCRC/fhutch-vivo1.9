"""
Fetch publications.
"""
from rdflib import Graph
from rdflib.namespace import RDF
import requests_cache

from converis import backend
from converis import client
from converis.namespaces import VIVO, CONVERIS
import utils
import models
import log_setup

logger = log_setup.get_logger()


requests_cache.install_cache(
    'data/cache_converis',
    allowable_methods=('GET', 'PUT')
)


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
    pub_ids = []
    g = Graph()
    for item in client.filter_query(q):
        g += client.to_graph(item, models.Publication)
        pub_ids.append(item.cid)
        if len(pub_ids) >= 50:
            break
    ng = "http://localhost/data/publications"
    backend.sync_updates(ng, g)
    return pub_ids


def generate_authorships(pub_ids):
    """
    Query for publications that are related to a particular person.
    """
    g = Graph()

    q = """
        <data xmlns="http://converis/ns/webservice">
        <query>
            <filter for="Publication" xmlns="http://converis/ns/filterengine" xmlns:ns2="http://converis/ns/sortingengine">
                <return>
                    <attributes>
                    </attributes>
                </return>
                <and>
                <relation name="PUBL_has_CARD">
                    <relation relatedto="{}" name="PERS_has_CARD">
                    </relation>
                </relation>
                </and>
            </filter>
        </query>
        </data>
    """
    logger.info("Generating authorships.")

    for cid, name in models.URL_IDX.items():
        count = 0
        for pc in client.filter_query(q.format(cid)):
            if pc.cid not in pub_ids:
                continue
            uri = models.hash_uri('aship', pc.cid + cid)
            person_uri = models.person_uri(cid)
            pub_uri = models.pub_uri(pc.cid)
            g.add((uri, RDF.type, VIVO.Authorship))
            g.add((uri, VIVO.relates, person_uri))
            g.add((uri, VIVO.relates, pub_uri))
            count += 1

        logger.info("Found {} pubs for {}.".format(count, name))

    utils.serialize_g(g, "authorship")


def harvest_pubs():
    pub_ids = []
    logger.info("Harvesting publication entities.")
    g = Graph()
    for item in client.filter_query(QUERY):
        g += client.to_graph(item, models.Publication)
        pub_ids.append(item.cid)

    utils.serialize_g(g, "publications")
    return pub_ids


def generate_orgs_to_pubs():
    """
    Relate pubs to orgs through publication cards.
    """
    top_org = "638881"

    internal_orgs_query = """
    <data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="Organisation" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
        <attribute operator="equals" argument="12000" name="intorext"/>
        <relation minCount="1" name="CARD_has_ORGA">
             <attribute operator="equals" argument="12006" name="typeOfCard"/>
         </relation>
      </filter>
     </query>
    </data>
    """

    pubs_for_org_query = """
    <data xmlns="http://converis/ns/webservice">
    <query>
        <filter for="Publication" xmlns="http://converis/ns/filterengine" xmlns:ns2="http://converis/ns/sortingengine">
            <return>
                <attributes>
                </attributes>
            </return>
            <and>
            <relation name="PUBL_has_CARD">
                <relation relatedto="{}" name="CARD_has_ORGA">
                </relation>
            </relation>
            </and>
        </filter>
    </query>
    </data>
    """
    logger.info("Fetching orgs with pub cards:\n" + internal_orgs_query)
    orgs = []
    for org in client.filter_query(internal_orgs_query):
        orgs.append(org.cid)
    org_set = set(orgs)

    logger.info("Relating {} orgs to pubs.".format(len(org_set)))
    g = Graph()
    for oid in org_set:
        if oid == top_org:
            continue
        logger.info("Processing orgs to pubs for org {}.".format(oid))
        q = pubs_for_org_query.format(oid)
        for pub in client.filter_query(q):
            ouri = models.org_uri(oid)
            pub_uri = models.pub_uri(pub.cid)
            logger.debug("Orgs to pubs. Processing org {} pub {}.".format(oid, pub.cid))
            g.add((ouri, VIVO.relates, pub_uri))

    utils.serialize_g(g, "org-pubs")


def full_publication_harvest():
    logger.info("Starting publications harvest.")
    pub_ids = harvest_pubs()
    generate_authorships(pub_ids)
    #logger.info("Adding local coauthor flag.")
    # generate_local_coauthor()
    # logger.info("Pub harvest and authorship generation complete.")
    logger.info("Relating orgs to publications.")
    generate_orgs_to_pubs()


if __name__ == "__main__":
    #sample_harvest()
    full_publication_harvest()
    #generate_orgs_to_pubs()
