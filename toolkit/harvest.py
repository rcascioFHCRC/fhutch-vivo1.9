import logging
import logging.handlers

from converis import backend
from converis import client
from converis.namespaces import D, VIVO, CONVERIS

# local models
import models

from rdflib import Graph, Literal

import requests_cache
requests_cache.install_cache(
   'converis',
   backend='redis',
   allowable_methods=('GET', 'PUT'))

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
)

# Set up a specific logger with our desired output level
logger = logging.getLogger("converis_client")
logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    "logs/harvest.log",
    maxBytes=10*1024*1024,
    backupCount=5,
)

logger.addHandler(handler)

def get_areas():
    q = """
    <data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="Area" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
      </filter>
     </query>
    </data>
    """
    g = Graph()
    for done, area in enumerate(client.filter_query(q)):
        g += client.to_graph(area, models.Expertise)
    return g


def get_pubs():
    q = """
    <data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="Publication" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
      <and>
        <and>
         <relation minCount="1" name="PUBL_has_CARD"/>
        </and>
        <and>
         <attribute argument="2009" name="publYear" operator="greaterequal"/>
        </and>
      </and>
      </filter>
     </query>
    </data>
    """
    g = Graph()
    done = 0
    for pub in client.filter_query(q):
        g += client.to_graph(pub, models.Publication)
        done += 1
    return g


def get_pub_cards():
    q = """
    <data xmlns="http://converis/ns/webservice">
      <return>
        <attributes>
        </attributes>
      </return>
     <query>
      <filter for="Card" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
      <and>
        <and>
            <relation minCount="1" name="PUBL_has_CARD"/>
        </and>
        <!-- <and>
            <relation name="PUBL_has_CARD">
                <attribute argument="2014" name="publYear" operator="greaterequal"/>
            </relation>
        </and> -->
      </and>
      </filter>
     </query>
    </data>
    """
    g = Graph()
    done = 0
    for card in client.filter_query(q):
        g += models.pub_to_card(card.cid)
        done += 1
        if (done % 200) == 0:
            logging.info("Publications fetched: {}.".format(done))
    return g


def get_orgs():
    internal = """
    <data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="Organisation" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
       <and>
        <attribute argument="12000" name="intOrExt" operator="equals"/>
       </and>
      </filter>
     </query>
    </data>
    """
    g = Graph()
    done = 0
    for q in [internal]:
        for org in client.filter_query(q):
            #if g.value(predicate=CONVERIS.converisId, object=Literal(org.cid)) is None:
            #    logging.debug("Mapping org {}.".format(org.cid))
            g += client.to_graph(org, models.Organization)
            done += 1
    return g


def get_people(sample=False):
    q = """
    <data xmlns="http://converis/ns/webservice">
     <return>
      <attributes>
       <attribute name="Short description"/>
       <attribute name="cfFamilyNames"/>
       <attribute name="cfFirstNames"/>
       <attribute name="middleName"/>
       <attribute name="email"/>
       <attribute name="ORCID"/>
       <attribute name="academicTitle"/>
       <attribute name="cfResInt"/>
      </attributes>
     </return>
     <query>
      <filter for="Person" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
       <and>
        <and>
         <attribute argument="12105" name="typeOfPerson" operator="equals"/>
        </and>
       </and>
      </filter>
     </query>
    </data>
    """
    g = Graph()
    done = 0
    for person in client.filter_query(q):
        g += client.to_graph(person, models.Person)
        done += 1
        if sample is True:
            if done >= 10:
                break
    return g

def harvest_people(sample=False):
    p = get_people(sample=sample)
    #print p.serialize(format='n3')
    backend.sync_updates("http://localhost/data/people", p)

def harvest_pubs():
    """
    Get publication entities.
    """
    p = get_pubs()
    #print p.serialize(format='n3')
    backend.post_updates("http://localhost/data/pubs", p)

def harvest_areas():
    """
    Gets all areas, narrower terms and any researchers
    associated with it.
    ~ 367
    """
    a = get_areas()
    #print a.serialize(format='n3')
    backend.sync_updates("http://localhost/data/areas", a)

def harvest_orgs():
    """
    Fetches all internal orgs and cards associated with those
    orgs.
    """
    g = get_orgs()
    #print g.serialize(format='n3')
    backend.sync_updates("http://localhost/data/orgs", g)


def harvest_journals():
    """
    Fetch all journals with pubs
    """
    q = """
    <data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="Journal" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
      <and>
        <and>
         <relation minCount="1" name="PUBL_has_JOUR"/>
        </and>
      </and>
      </filter>
     </query>
    </data>
    """
    g = Graph()
    done = 0
    for pub in client.filter_query(q):
        g += client.to_graph(pub, models.Journal)
        done += 1
    #print g.serialize(format='n3')
    backend.sync_updates("http://localhost/data/journals", g)

if __name__ == "__main__":
    harvest_people()
    harvest_orgs()
    harvest_areas()
    harvest_journals()
