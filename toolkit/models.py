"""
VIVO models
"""
import hashlib
import logging
import re
import os

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.resource import Resource
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL

from converis import client
from converis.namespaces import rq_prefixes
from converis.namespaces import D, BIBO, VIVO, OBO, VCARD, CONVERIS, SKOS

from converis.backend import SyncVStore

# display classes
FHD = Namespace('http://vivo.fredhutch.org/ontology/display#')
# publications
FHP = Namespace('http://vivo.fredhutch.org/ontology/publications#')
# trials
FHCT = Namespace('http://vivo.fredhutch.org/ontology/clinicaltrials#')

DATA_NAMESPACE = D

logger = logging.getLogger("converis_client")

def person_uri(person_id):
    return D['c' + person_id]

def org_uri(cid):
    return D['c' + cid]

def card_uri(cid):
    return D['c' + cid]

def pub_uri(cid):
    return D['c' + cid]

def area_uri(cid):
    return D['c' + cid]

def journal_uri(cid):
    return D['c' + cid]

def hash_uri(prefix, value):
    return D[prefix + '-' + hashlib.md5(value).hexdigest()]


class BaseModel(client.BaseEntity):
    @property
    def vid(self):
        """
        VIVO ID. Must start with letter.
        """
        return "c" + self.cid

    @property
    def uri(self):
        return URIRef(D + self.vid)


class Person(BaseModel):
    """
    A Converis person.
    """
    @property
    def vcard_uri(self):
        return DATA_NAMESPACE + "vci" + self.vid

    @property
    def vcard_name_uri(self):
        return DATA_NAMESPACE + "vcn" + self.vid

    @property
    def vcard_title_uri(self):
        return URIRef(DATA_NAMESPACE + "vct" + self.vid)

    @property
    def vcard_email_uri(self):
        return URIRef(DATA_NAMESPACE + "vce" + self.vid)

    @property
    def vcard_phone_uri(self):
        return URIRef(DATA_NAMESPACE + "vcp" + self.vid)

    @property
    def _first(self):
        """
        Use nickname for first name if it's present per AMC.
        """
        if hasattr(self, 'nickname'):
            first = self.nickname
        else:
            first = self.cffirstnames
        return first

    @property
    def orcid_uri(self):
        if self.orcid:
            try:
                return URIRef('http://orcid.org/' + self.orcid)
            except AttributeError:
                return

    def get_positions(self):
        """
        Add positions. If position is a pub-tracking card
        then just add as a data attribute.
        """
        g = Graph()
        cards = client.RelatedObject('Person', self.cid, 'PERS_has_CARD')
        for card in cards:
            # Check for pub tracking cards.
            if (hasattr(card, 'positiontype') is True) and\
                 (card.positiontype.get('cid') == '12166'):
                g.add((self.uri, CONVERIS.pubCardId, Literal(card.cid)))
                continue
            # Skip external cards for now
            # if (hasattr(card, 'typeofcard') is True) and\
            #     (card.typeofcard.get('cid') == '12007'):
            #    continue
            # Skip cards that aren't current
            if (hasattr(card, 'currentposition') is True) and\
                 (card.currentposition.get('cid') != '11288'):
                continue
            g += client.to_graph(card, Position)
            g.add((self.uri, VIVO.relatedBy, card_uri(card.cid)))
        return g

    def _label(self):
        l = "{}, {}".format(self.cffamilynames, self._first)
        if hasattr(self, 'middlename'):
            l + " " + self.middlename
        return l


    def to_rdf(self):
        g = Graph()
        p = Resource(g, self.uri)
        p.add(RDF.type, FOAF.Person)
        p.set(RDFS.label, Literal(self._label()))
        p.set(CONVERIS.converisId, Literal(self.cid))
        if hasattr(self, 'cfresint'):
            p.set(VIVO.researchOverview, Literal(self.cfresint))
        if hasattr(self, 'orcid'):
            p.set(FHD.orcid, Literal(self.orcid))
        # clinical interests
        if hasattr(self, 'cfclinint'):
            p.set(FHD.clinicalInterest, Literal(self.cfclinint))
        # brief description
        if hasattr(self, 'briefdescription'):
            p.set(FHD.briefDescription, Literal(self.briefdescription))

        # Vcard individual
        vci_uri = URIRef(self.vcard_uri)
        p.set(OBO['ARG_2000028'], vci_uri)
        g.add((vci_uri, RDF.type, VCARD.Individual))

        # Vcard Name
        g += self._vcard_name()
        g.add((vci_uri, VCARD.hasName, URIRef(self.vcard_name_uri)))

        # Vcard title
        vtg = self._vcard_title()
        if vtg is not None:
            g += vtg
            g.add((vci_uri, VCARD.hasTitle, URIRef(self.vcard_title_uri)))

        # Vcard email
        vte = self._vcard_email()
        if vte is not None:
            g += vte
            g.add((vci_uri, VCARD.hasEmail, URIRef(self.vcard_email_uri)))

        # Vcard phone
        vtp = self._vcard_phone()
        if vtp is not None:
            g += vtp
            g.add((vci_uri, VCARD.hasTelephone, URIRef(self.vcard_phone_uri)))

        # positions
        g += self.get_positions()

        # videos
        g += self.get_videos()

        # add single letter sort key for person browse
        p.set(FHD.sortLetter, Literal(self._label()[0].lower()))

        return g

    def _vcard_name(self):
        g = Graph()
        vc = Resource(g, URIRef(self.vcard_name_uri))
        vc.set(RDF.type, VCARD.Name)
        vc.set(RDFS.label, Literal(self._label()))
        vc.set(VCARD.familyName, Literal(self.cffamilynames))
        vc.set(VCARD.givenName, Literal(self._first))
        if hasattr(self, 'middlename'):
            vc.set(VIVO.middleName, Literal(self.middlename))
        return g

    def _vcard_title(self):
        #if not hasattr(self, 'academictitle'):
        #    return None
        sdesc = self.shortdescription
        title = ", ".join([sd.strip() for sd in sdesc.split(',')[1:]])
        if title == "":
            return None
        g = Graph()
        vt = Resource(g, self.vcard_title_uri)
        vt.set(RDF.type, VCARD.Title)
        vt.set(RDFS.label, Literal(title))
        vt.set(VCARD.title, Literal(title))
        return g

    def _vcard_email(self):
        if not hasattr(self, 'email'):
            return None
        g = Graph()
        vt = Resource(g, self.vcard_email_uri)
        vt.set(RDF.type, VCARD.Work)
        # Label probably not necessary
        vt.set(RDFS.label, Literal(self.email))
        vt.set(VCARD.email, Literal(self.email))
        return g

    def _vcard_phone(self):
        if not hasattr(self, 'phone'):
            return None
        g = Graph()
        vt = Resource(g, self.vcard_phone_uri)
        vt.set(RDF.type, VCARD.Voice)
        # Label probably not necessary
        vt.set(RDFS.label, Literal(self.phone))
        vt.set(VCARD.telephone, Literal(self.phone))
        return g

    def get_videos(self):
        # URL regex from http://stackoverflow.com/a/6883094/758157
        g = Graph()
        if hasattr(self, "embeddedvideos"):
            text = self.embeddedvideos
            #for link in re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
            for link in text.split(';'):
                cl = link.strip().replace('&quot;', "")
                if cl == "":
                    continue
                g.add((self.uri, FHD.video, Literal(cl)))
            return g
        return g


class Position(BaseModel):

    def _date(self, dtype, dv):
        g = Graph()
        date_obj = client.convert_date(dv)
        date_uri = URIRef(DATA_NAMESPACE + 'date' + dtype + self.vid)
        de = Resource(g, date_uri)
        de.set(RDF.type, VIVO.DateTimeValue)
        if date_obj is not None:
            de.set(RDFS.label, Literal(dv))
            de.set(
                VIVO.dateTime,
                Literal(date_obj, datatype=XSD.date)
            )
            de.set(VIVO.dateTimePrecision, VIVO.yearMonthDayPrecision)
        return date_uri, g

    def get_dti(self, start, end):
        if (start is None) and (end is None):
            return
        # Date/Time Interval
        g = Graph()
        dti_uri = D['dti'] + self.vid
        dti = Resource(g, dti_uri)
        dti.set(RDF.type, VIVO.DateTimeInterval)
        if start is not None:
            start_uri, start_g = self._date("start", start)
            dti.set(VIVO.start, start_uri)
            g += start_g
        if end is not None:
            end_uri, end_g = self._date("end", end)
            g += end_g
            dti.set(VIVO.end, end_uri)
        return dti_uri, g


    def get_people(self):
        """
        Add positions. If position is a pub-tracking card
        then just add as a data attribute.
        """
        g = Graph()
        people = client.get_related_ids('Person', self.cid, 'PERS_has_CARD')
        for person in people:
            # A position relates a person
            g.add((self.uri, VIVO.relates, person_uri(person)))
        return g

    def get_orgs(self):
        """
        Get orgs for the positions.
        """
        g = Graph()
        for org in client.get_related_ids('Organisation', self.cid, 'CARD_has_ORGA'):
            g.add((self.uri, VIVO.relates, org_uri(org)))
        return g

    def add_type_rank(self):
        """
        Position type.
        """
        g = Graph()
        r = Resource(g, self.uri)
        try:
            ptype = self.positiontype['cid']
        except AttributeError:
            ptype = None
        # Leadership
        if ptype == '12169':
            r.set(RDF.type, VIVO.FacultyAdministrativePosition)
            r.set(VIVO.rank, Literal(10, datatype=XSD.integer))
        # Faculty
        elif ptype == '12167':
            r.set(RDF.type, VIVO.FacultyPosition)
            r.set(VIVO.rank, Literal(20, datatype=XSD.integer))
        elif ptype == '12007':
            r.set(RDF.type, FHD.ExternalPosition)
            r.set(VIVO.rank, Literal(60, datatype=XSD.integer))
        else:
            r.set(RDF.type, VIVO.Position)
            r.set(VIVO.rank, Literal(30, datatype=XSD.integer))
        return g

    def to_rdf(self):
        g = Graph()
        g += self.add_type_rank()
        e = Resource(g, self.uri)
        e.set(CONVERIS.converisId, Literal(self.cid))
        # Check jobtitle and function for position name.
        if hasattr(self, 'jobtitle'):
            title = self.jobtitle
        elif hasattr(self, 'function'):
            title = self.function['value']
        else:
            title = "Research"
        e.set(RDFS.label, Literal(title))
        # start/end
        try:
            start = self.cfstartdate
        except AttributeError:
            start = None
            pass
        try:
            end = self.cfenddate
        except AttributeError:
            end = None
            pass
        # Add datetime interval
        try:
            dti_uri, dti_g = self.get_dti(start, end)
            g += dti_g
            e.set(VIVO.dateTimeInterval, dti_uri)
        except TypeError:
            pass

        # map to people
        #g += self.get_people()
        # map to orgs
        #g += self.get_orgs()
        # people go to positions
        # orgs go to positions

        return g


class Organization(BaseModel):


    def related_uri(self, c_id):
        return D['c' + c_id]

    def get_children(self):
        """
        Get sub-organizations.
        """
        out = []
        for org in client.get_related_ids("Organisation", self.cid, "ORGA_has_child_ORGA"):
            out.append(self.related_uri(org))
        return out

    def get_positions(self):
        g = Graph()
        # skip these orgs
        #if self.cid in ['494698', '494815']:
        #    return g
        for card in client.get_related_ids('Card', self.cid, 'CARD_has_ORGA'):
            g.add((self.uri, VIVO.relatedBy, card_uri(card)))
        return g

    def get_url(self):
        g = Graph()
        try:
            if self.cfuri is not None:
                g.add((self.uri, FHD.url, Literal(self.cfuri)))
            return g
        except AttributeError:
            return g

    def get_type(self):
        # Map of Converis type of org to VIVO class.
        m = {
            '11739': FHD.CoreFacilities,
            '11734': FHD.Department,
            '11736': FHD.Division,
            '11733': FHD.Faculty,
            '11735': FHD.Group,
            '11738': FHD.Lab,
            '11737': FHD.Program,
            '11740': FHD.ScientificInitiative,
            '11731': FHD.SharedResource,
            '11732': FHD.Study,
        }
        try:
            otype = self.typeoforga['cid']
            oty = m.get(otype, FHD.Organization)
            return oty
        except AttributeError:
            return FHD.Organization

    def add_vcard_weblink(self):
        """
        Build statements for weblinks in VIVO.
        :return: rdflib.Graph
        """
        g = Graph()
        try:
            if self.cfuri is not None:
                url = self.cfuri
        except AttributeError:
            return g

        # vcard individual for org
        vci_uri = D['vcard-individual-org-' + self.cid]
        g.add((vci_uri, RDF.type, VCARD.Individual))

        # vcard URL
        vcu_uri = D['vcard-url-org-' + self.cid]
        g.add((vcu_uri, RDF.type, VCARD.URL))
        g.add((vcu_uri, RDFS.label, Literal(u"organization's website")))
        g.add((vcu_uri, VCARD.url, Literal(url)))

        # Relate vcard individual to url
        g.add((vci_uri, VCARD.hasURL, vcu_uri))
        # Relate web link and org
        g.add((self.uri, OBO['ARG_2000028'], vci_uri))
        return g


    def to_rdf(self, get_all=True):
        g = Graph()
        o = Resource(g, self.uri)
        o.set(RDF.type, self.get_type())
        o.set(RDFS.label, Literal(self.cfname))
        o.set(CONVERIS.converisId, Literal(self.cid))
        if hasattr(self, 'description'):
            o.set(VIVO.overview, Literal(self.description))

        if get_all is True:
            for child in self.get_children():
                # Has sub-organization
                o.add(OBO['BFO_0000051'], child)
            # Get positions for this org.
            g += self.get_positions()

        g += self.add_vcard_weblink()
        return g


class Publication(BaseModel):

    def get_type(self, default=FHP.OtherPublication):
        """
        Assign a publication type.
        Based on Fred Hutch types.
        """
        ptypes = {
            "Journal article": BIBO.AcademicArticle,
            "Article or Abstract": BIBO.AcademicArticle,
            "Book": BIBO.Book,
            "Book Chapter or Entry": BIBO.BookChatper,
            "Dataset": VIVO.Dataset,
            "Dissertation or Thesis": BIBO.Thesis,
            "Internet Communication": BIBO.Webpage,
            "Report": BIBO.Report,
            "Book Chapter Abstract": BIBO.BookChapter,
            "Book review": VIVO.Review,
            "Conference proceedings": BIBO.Proceedings,
            "Conference proceedings article": BIBO.Proceedings,
        }
        ptypes = {
            '10357': FHP.ArticleAbstract,
            '10347': FHP.Book,
            '10346': FHP.BookChapterEntry,
            '10242': FHP.Dataset,
            '10341': FHP.DissertationThesis,
            '10336': FHP.InternetCommunication,
            '10348': FHP.Multimedia,
            '10335': FHP.NewsItem,
            '10358': FHP.Poster,
            '10359': FHP.Presentation,
            '10324': FHP.Report,
            '10343': FHP.SoftwareCode,
            '10323': FHP.OtherPublication,
        }
        if hasattr(self, 'publicationtype'):
            ctype = self.publicationtype['cid'].strip()
            return ptypes.get(ctype, default)
        return default

    def data_properties(self):
        props = [
            ('srcauthors', CONVERIS.authorList),
            ('doi', BIBO.doi),
            ('pubmedid', BIBO.pmid),
            ('pmcid', VIVO.pmcid),
            ('isiid', CONVERIS.wosId),
            ('cfstartpage', BIBO.start),
            ('cfendpage', BIBO.end),
            ('cfabstr', BIBO.abstract),
            ('cfvol', BIBO.volume),
            ('cfissue', BIBO.issue),
            ('cftotalpages', BIBO.numPages),
            ('shortdescription', CONVERIS.citationText)
        ]
        for k, pred in props:
            if hasattr(self, k):
                value = getattr(self, k).strip()
                # skip blanks
                if value == u"":
                    continue
                yield (pred, Literal(value))

    def add_date(self):
        # cfResPublDate
        g = Graph()
        date_value = None
        year_value = None
        if hasattr(self, 'cfrespubldate'):
            date_value = self.cfrespubldate
        if hasattr(self, 'publyear'):
            year_value = self.publyear

        if (date_value is None) and (year_value is None):
            return g

        date_uri = URIRef(DATA_NAMESPACE + 'pubdate' + self.cid)
        de = Resource(g, date_uri)
        de.set(RDF.type, VIVO.DateTimeValue)
        if date_value is not None:
            de.set(RDFS.label, Literal(date_value))
            de.set(
                VIVO.dateTime,
                Literal("{}T00:00:00".format(date_value), datatype=XSD.dateTime)
            )
            de.set(VIVO.dateTimePrecision, VIVO.yearMonthDayPrecision)
        else:
            clean = year_value.strip().replace(',', '')
            de.set(RDFS.label, Literal(clean))
            de.set(
                VIVO.dateTime,
                Literal("{}-01-01T00:00:00".format(clean), datatype=XSD.dateTime)
            )
            de.set(VIVO.dateTimePrecision, VIVO.yearPrecision)

        g.add((self.uri, VIVO.dateTimeValue, date_uri))
        return g

    def pub_cards(self):
        g = Graph()
        for card in client.get_related_ids('Card', self.cid, 'PUBL_has_CARD'):
            g.add((self.uri, CONVERIS.pubCardId, Literal(card)))
        return g


    def to_rdf(self):
        g = Graph()
        o = Resource(g, self.uri)
        o.set(RDF.type, self.get_type())
        o.set(CONVERIS.converisId, Literal(self.cid))
        try:
            o.set(RDFS.label, Literal(self.cftitle))
        except AttributeError:
            logger.error("Can't find title for {}".format(self.cid))
            return g
        for pred, obj in self.data_properties():
            o.set(pred, obj)

        # add date
        g += self.add_date()

        return g


class Expertise(BaseModel):

    def has_researchers(self):
        g = Graph()
        for person in client.get_related_ids('Person', self.cid, 'PERS_has_AREA'):
            puri = person_uri(person)
            g.add((self.uri, VIVO.researchAreaOf, puri))
        return g

    def has_orgs(self):
        g = Graph()
        for org in client.get_related_ids('Organisation', self.cid, 'ORGA_has_AREA'):
            uri = org_uri(org)
            g.add((self.uri, VIVO.researchAreaOf, uri))
        return g

    def get_narrower(self):
        g = Graph()
        for area in client.get_related_ids('Area', self.cid, 'AREA_has_child_AREA'):
            narrow = area_uri(area)
            g.add((self.uri, SKOS.narrower, narrow))
        return g

    def add_primary_type(self):
        """
        Use short description to identify what tree
        the term is in.

        Should we skip the parent concepts so they
        don't appear in the browse?

        """
        g = Graph()
        etype = FHD.Expertise
        if hasattr(self, "shortdesription"):
            sd = self.shortdescription
            if "Research and Clinical Topics" in sd:
                etype = FHD.ResearchClinicalTopics
            elif "Disciplines" in sd:
                etype = FHD.Disciplines
        g.add((self.uri, RDF.type, etype))
        return g

    def to_rdf(self):
        g = Graph()
        r = Resource(g, self.uri)
        r.set(RDFS.label, Literal(self.name))
        r.set(CONVERIS.converisId, Literal(self.cid))

        # Set local class
        g += self.add_primary_type()
        # Get related researchers
        g += self.has_researchers()
        # Get related orgs
        g += self.has_orgs()
        # Ger narrower terms.
        g += self.get_narrower()

        return g


class Journal(BaseModel):

    def get_venue_for(self):
        g = Graph()
        for pub in client.get_related_ids('Publication', self.cid, 'PUBL_has_JOUR'):
            puri = pub_uri(pub)
            g.add((self.uri, VIVO.publicationVenueFor, puri))
        return g


    def to_rdf(self):
        g = Graph()
        r = Resource(g, self.uri)
        r.set(RDF.type, BIBO.Journal)
        r.set(RDFS.label, Literal(self.name))
        r.set(CONVERIS.converisId, Literal(self.cid))

        if hasattr(self, 'issn'):
            r.set(BIBO.issn, Literal(self.issn))
        if hasattr(self, 'eissn'):
            r.set(BIBO.eissn, Literal(self.eissn))

        g += self.get_venue_for()

        return g


class News(BaseModel):

    def get_type(self, default=FHD.News):
        """
        """
        ntypes = {
            '10267': FHD.HutchNews,
            '10268': FHD.MediaCoverage,
        }
        if hasattr(self, 'typeofnews'):
            ctype = self.typeofnews['cid'].strip()
            return ntypes.get(ctype, default)
        return default

    def add_vcard_weblink(self):
        """
        Build statements for weblinks in VIVO.
        :return: rdflib.Graph
        """
        g = Graph()
        try:
            if self.url is not None:
                url = self.url
        except AttributeError:
            return g

        # vcard individual for org
        vci_uri = D['vcard-individual-news-' + self.cid]
        g.add((vci_uri, RDF.type, VCARD.Individual))

        # vcard URL
        vcu_uri = D['vcard-url-news-' + self.cid]
        g.add((vcu_uri, RDF.type, VCARD.URL))
        g.add((vcu_uri, RDFS.label, Literal(u"view item")))
        g.add((vcu_uri, VCARD.url, Literal(url)))

        # Relate vcard individual to url
        g.add((vci_uri, VCARD.hasURL, vcu_uri))
        # Relate web link and org
        g.add((self.uri, OBO['ARG_2000028'], vci_uri))
        return g

    def get_news_subject(self):
        g = Graph()
        for person in client.get_related_ids('Person', self.cid, 'NEWS_has_PERS'):
            puri = person_uri(person)
            g.add((self.uri, FHD.featuresResearcher, puri))
        return g

    def get_features(self):
        g = Graph()
        for pub in client.get_related_ids('Publication', self.cid, 'NEWS_has_PUBL'):
            puri = pub_uri(pub)
            g.add((self.uri, FHD.featuresPublication, puri))
        return g

    def add_date(self):
        g = Graph()
        if hasattr(self, 'publishedon'):
            date_obj = client.convert_date(self.publishedon)
            g.add((self.uri, FHD.publishedOn, Literal(date_obj, datatype=XSD.date)))
        return g

    def to_rdf(self):
        g = Graph()
        r = Resource(g, self.uri)
        r.set(RDF.type, self.get_type())
        r.set(RDFS.label, Literal(self.title))
        r.set(CONVERIS.converisId, Literal(self.cid))

        if hasattr(self, 'url'):
            r.set(FHD.url, Literal(self.url))

        g += self.get_news_subject()
        g += self.get_features()
        g += self.add_date()

        #g += self.add_vcard_weblink()

        return g


def pub_to_card(card_id):
    g = Graph()
    for pub in client.get_related_ids('Publication', card_id, 'PUBL_has_CARD'):
        #ashipuri = D['aship-{}-{}'.format(pub, self.cid)]
        puri = pub_uri(pub)
        g.add((puri, CONVERIS.pubCardId, Literal(card_id)))
    return g


def create_authorships():
    q = """
    select DISTINCT ?person ?publication
    where {
        ?person a foaf:Person ;
                converis:pubCardId ?card .
        ?publication a <http://vivo.fredhutch.org/ontology/publications#Publication> ;
            converis:pubCardId ?card .
    }
    """
    #Define the VIVO store
    query_endpoint = os.environ['VIVO_URL'] + '/api/sparqlQuery'
    update_endpoint = os.environ['VIVO_URL'] + '/api/sparqlUpdate'
    vstore = SyncVStore(
                os.environ['VIVO_EMAIL'],
                os.environ['VIVO_PASSWORD']
            )
    vstore.open((query_endpoint, update_endpoint))

    g = Graph()
    query = rq_prefixes + q
    for row in vstore.query(query):
        uri = hash_uri("authorship", row.person.toPython() + row.publication.toPython())
        g.add((uri, RDF.type, VIVO.Authorship))
        g.add((uri, VIVO.relates, row.person))
        g.add((uri, VIVO.relates, row.publication))
    return g


def get_pub_cards():
    q = """
    select DISTINCT ?card
    where {
        ?person a foaf:Person ;
            converis:pubCardId ?card .
    }
    """
    #Define the VIVO store
    query_endpoint = os.environ['VIVO_URL'] + '/api/sparqlQuery'
    update_endpoint = os.environ['VIVO_URL'] + '/api/sparqlUpdate'
    vstore = SyncVStore(
                os.environ['VIVO_EMAIL'],
                os.environ['VIVO_PASSWORD']
            )
    vstore.open((query_endpoint, update_endpoint))

    query = rq_prefixes + q
    out = []
    for row in vstore.query(query):
        out.append(row.card.toPython())
    return set(out)

class ClinicalTrial(BaseModel):

    def get_sponsors(self):
        """
        Create basic org RDF for sponsors in the event that they
        aren't an internal org.
        """
        g = Graph()
        for org in client.get_related_entities('Organisation', self.cid, 'CLIN_has_ORGA'):
            ouri = org_uri(org.cid)
            g.add((self.uri, FHCT.hasSponsor, ouri))
            # org model
            om = Organization(**org.__dict__)
            # don't fetch positions for these orgs.
            g += om.to_rdf(get_all=False)

        return g

    def get_pubs(self):
        g = Graph()
        for pub in client.get_related_ids('Publication', self.cid, 'CLIN_has_PUBL'):
            uri = pub_uri(pub)
            g.add((self.uri, FHCT.trialPublication, uri))
        return g

    def get_investigators(self):
        g = Graph()
        for pub in client.get_related_ids('Person', self.cid, 'CLIN_has_PERS'):
            uri = pub_uri(pub)
            g.add((self.uri, FHCT.hasInvestigator, uri))
        return g

    def assign_type(self):
        default = FHCT.Other
        ttypes = {
            '5340473': FHCT.ActiveNotRecruiting,
            '5340476': FHCT.ApprovedForMarketing,
            '5340479': FHCT.AvailableForExpandedAccess,
            '5340482': FHCT.Completed,
            '5340485': FHCT.EnrollingByInvitation,
            '5340488': FHCT.NoLongerAvailableForExpandedAccess,
            '5340491': FHCT.NotYetRecruiting,
            '5340494': FHCT.Recruiting,
            '5340497': FHCT.Suspended,
            '5340500': FHCT.TemporarilyNotAvailableForExpandedAccess,
            '5340503': FHCT.Terminated,
            '5340506': FHCT.Withdrawn,
        }
        if hasattr(self, 'recruitmentstatus'):
            ctype = self.recruitmentstatus['cid'].strip()
            return ttypes.get(ctype, default)
        return default

    def to_rdf(self):
        g = Graph()
        r = Resource(g, self.uri)
        r.set(RDF.type, self.assign_type())
        try:
            r.set(RDFS.label, Literal(self.brieftitle))
        except AttributeError:
            logger.warning("No brief title found for trial {}".format(self.cid))
            return Graph()
        r.set(FHCT.officialTitle, Literal(self.officialtitle))
        r.set(CONVERIS.converisId, Literal(self.cid))

        if hasattr(self, "briefsummary"):
            r.set(VIVO.overview, Literal(self.briefsummary))

        r.set(FHCT.nctNumber, Literal(self.nctnumber))
        r.set(FHD.url, Literal(self.url))

        g += self.get_sponsors()
        g += self.get_pubs()
        g += self.get_investigators()

        return g
