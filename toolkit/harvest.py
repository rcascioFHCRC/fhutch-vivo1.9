import logging

from converis import backend
from converis import client
from converis import models
from converis.namespaces import D, VIVO, CONVERIS

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


def get_areas():
    q = """
    <data xmlns="http://converis/ns/webservice">
     <query>
      <filter for="Area" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
      <or>
        <and>
         <relation minCount="1" name="PERS_has_AREA"/>
        </and>
      </or>
      </filter>
     </query>
    </data>
    """
    g = Graph()
    for done, area in enumerate(converis.filter_query(q)):
        g += converis.to_graph(area, models.Area)
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
         <attribute argument="2016" name="publYear" operator="greaterequal"/>
        </and>
      </and>
      </filter>
     </query>
    </data>
    """
    g = Graph()
    done = 0
    for pub in converis.filter_query(q):
        g += converis.to_graph(pub, models.Publication)
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
        <and>
            <relation name="PUBL_has_CARD">
                <attribute argument="2014" name="publYear" operator="greaterequal"/>
            </relation>
        </and>
      </and>
      </filter>
     </query>
    </data>
    """
    g = Graph()
    done = 0
    for card in converis.filter_query(q):
        g += models.pub_to_card(card.cid)
        done += 1
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


def get_people():
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
    for person in converis.filter_query(q):
        g += converis.to_graph(person, models.Person)
        done += 1

    #print g.serialize(format="n3")
    return g

def harvest_people():
    p = get_people()
    backend.sync_updates("http://localhost/data/people", p)

def harvest_pubs():
    p = get_pubs()
    p += get_pub_cards()
    print p.serialize(format='n3')
    #backend.post_updates("http://localhost/data/pubs", p)

def harvest_areas():
    a = get_areas()
    #print a.serialize(format='n3')
    backend.post_updates("http://localhost/data/areas", a)

def harvest_orgs():
    g = get_orgs()
    print g.serialize(format='n3')
    #backend.sync_updates("http://localhost/data/orgs", g)

if __name__ == "__main__":
    #people, orgs = harvest()
    harvest_orgs()
    #harvest_areas()
    #print g.serialize(format='n3')
    #harvest_pubs()
    #print pubs.serialize(format='n3')
    #backend.create_authorships()
    
    #backend.sync_updates("http://localhost/data/orgs", orgs)
    #backend.sync_updates("http://localhost/data/pubs", pubs)
    # import sys
    # pid = sys.argv[1]

    # cty = converis.Entity('Person', pid)
    # g = converis.to_graph(cty, models.Person)
    # print g.serialize(format="n3")
    # backend.post_updates("http://localhost/data/people", g)