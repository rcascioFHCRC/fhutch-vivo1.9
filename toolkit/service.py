"""
Service harvest process.
"""
import os
import logging
import logging.handlers

from converis import backend
from converis import client

# local models
import models
import log_setup

from utils import ThreadedHarvest

from rdflib import Graph

logger = log_setup.get_logger()

if os.environ.get('HTTP_CACHE') == "1":
  import requests_cache
  requests_cache.install_cache(
     'converis',
     backend='redis',
     allowable_methods=('GET', 'PUT'))

THREADS = int(os.environ['THREADS'])

NG = "http://localhost/data/service"

from models import (
  BaseModel,
  FHS,
  FHD,
  VIVO,
  Resource,
  Literal,
  RDF,
  RDFS,
  person_uri,
  org_uri
)

class Service(BaseModel):

    def _v(self, k):
        value = None
        if hasattr(self, k):
            try:
                value = getattr(self, k).strip()
            except AttributeError:
                # these are choice groups
                value = getattr(self, k)['value'].strip()
            # skip blanks
            if value == u"":
                return
        return value

    def get_type(self, default=FHS.Service):
        """
        10441
        Consultant Services
            
        10443
        Editorial or Review
            
        10447
        Foundations and Trusts
            
        10445
        Industry
            
        10446
        Government Entity or NGO Service
            
        10444
        Professional and Honors Societies
            
        10442
        University or Institutional Services
	
        15983752
        Meeting Attendance or Presentation
        """
        ntypes = {
            '10441': FHS.ConsultantServices,
            '10443': FHS.EditorialReview,
            '10447': FHS.FoundationsTrusts,
            '10445': FHS.Industry,
            '10446': FHS.NationalInternationalService,
            '10444': FHS.ProfessionalHonorsSocieties,
            '10442': FHS.UniversityInstitutionalServices,
            '15983752': FHS.MeetingAttendancePresentation
        }
        if hasattr(self, 'dynamictype'):
            ctype = self.dynamictype['cid'].strip()
            return ntypes.get(ctype, default)
        return default


    def get_person(self):
        g = Graph()
        for person in client.get_related_ids('Person', self.cid, 'SERV_has_PERS'):
            puri = person_uri(person)
            g.add((self.uri, VIVO.relates, puri))
        return g

    def get_org(self):
        #g = Graph()
        for org in client.get_related_entities('Organisation', self.cid, 'SERV_has_ORGA'):
            return org.cfname
            #puri = org_uri(org)
            #g.add((self.uri, VIVO.relates, puri))
        return

    def get_journal(self):
        g = Graph()
        name = None
        for jrnl in client.RelatedObject('Service', self.cid, 'SERV_has_JOUR'):
            juri = models.journal_uri(jrnl.cid)
            g.add((self.uri, VIVO.relates, juri))
            jm = models.Journal(**jrnl.__dict__)
            name = jrnl.name
            g += jm.to_rdf()
        return name, g

    def related_event(self):
        events = client.get_related_entities('cfEvent', self.cid, 'SERV_has_EVEN')
	for ev in events:
	    return ev.shortdescription
	return None

    def _gattrs(self, keys):
        for key in keys:
            if hasattr(self, key):
                val = getattr(self, key)
                if type(val) == dict:
                    return getattr(self, key)['value']
                else:
                    return val
        return None

    def label(self):
        """
        Look in various fields for role description.
        """
        role = self._gattrs([
            "prosocietyrole",
            "editorshiprole",
	    "meetingrole",
            #"committeerole",
            "description"
            #"roleother",
            "consultantactivityother"
        ]
        ) or ""
        modifier = None
        if hasattr(self, "rolemodifier"):
            modifier = self.rolemodifier["value"]
            role = u"{} {}".format(modifier, role)
        if hasattr(self, "committeerole"): #and hasattr(self, "roleother")
            #if self.committeerole["value"] == "Other":
            role += u"{}".format(self.committeerole["value"])
            if role == 'Other' and hasattr(self, "roleother"):
                role = u"{}".format(self.roleother)
        elif hasattr(self, "roleother"):
            role += u"{}".format(self.roleother)
	if hasattr(self, "title"):
            role += u"{}".format(self.title)
        if hasattr(self, "committeegroup"):
			if not role:
				role = u"{}".format(self.committeegroup)
			else:
				role += u", {}".format(self.committeegroup)
        if hasattr(self, "consultantactivity"):
            role += u", {}".format(self.consultantactivity["value"])
	if hasattr(self, "journalother"):
            role += u", {}".format(self.journalother)
        return role


    def full_label(self):
        lb = [
            self.label(),
	    self.related_event()
        ]
        lb.append(self.related_org_label("SERV_has_ORGA"))
        label = ", ".join([l for l in lb if l is not None and l != ""])
        return Literal(label)


    def to_rdf(self):
        g = Graph()
        r = Resource(g, self.uri)
        vtype = self.get_type()
        label = self.full_label()
        if vtype == FHS.MeetingAttendancePresentation:
            # label = label.replace("Member, ", "")
            # debugging consultant activity
            logger.info('Label: %s.' % (label))
        r.set(RDF.type, vtype)
        r.set(RDFS.label, Literal(label))
        r.set(FHD.converisId, Literal(self.cid))

        g += self.get_person()
        #g += self.get_org()
        jname, jg = self.get_journal()
        g += jg

        if hasattr(self, 'startedon'):
            start = self.startedon
        else:
            start = None

        if hasattr(self, "endedon"):
            end = self.endedon
        else:
            end = None
        # Add datetime interval
        try:
            dti_uri, dti_g = self._dti(start, end)
            g += dti_g
            r.set(VIVO.dateTimeInterval, dti_uri)
        except TypeError:
            pass

        #g += self.add_vcard_weblink()

        return g


service_q = """
<data xmlns="http://converis/ns/webservice">
 <query>
  <filter for="Service" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
  </filter>
 </query>
</data>
"""


def harvest_service(sample=False):
    """
    Fetch all service items
    """
    g = Graph()
    done = 0
    for item in client.filter_query(service_q):
        #print item.cid
        logger.error(item.cid)
        g += client.to_graph(item, Service)
        done += 1
        if (sample is True) and (done >= 100):
            break
    print g.serialize(format='n3')
    backend.sync_updates(NG, g)


class ServiceHarvest(ThreadedHarvest):

    def __init__(self, q, vmodel, threads=THREADS):
        self.query = q
        self.graph = Graph()
        self.threads = threads
        self.vmodel = vmodel
        #self.page_size = 30


def harvest():
    jh = ServiceHarvest(service_q, Service)
    jh.run_harvest()
    logger.info("Service harvest finished. Syncing to vstore.")
    jh.sync_updates(NG)

if __name__ == "__main__":
    logger.info("Starting Service harvest.")
    harvest()
    #harvest_service(sample=True)
    logger.info("Service harvest complete.")
