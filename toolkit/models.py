"""
VIVO models
"""
import logging

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.resource import Resource
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL

import converis
from namespaces import D, BIBO, VIVO, OBO, VCARD, CONVERIS, SKOS

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

class BaseModel(converis.BaseEntity):
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
        # for card_id in converis.get_related_ids('Card', self.cid, "PERS_has_CARD"):
        #     pos_obj = Position(cid=card_id)
        #     g.add((self.uri, VIVO.relatedBy, pos_obj.uri))
        # return g
        cards = converis.RelatedObject('Person', self.cid, 'PERS_has_CARD')
        for card in cards:
            try:
                # Check for pub tracking cards first.
                ptype = card.positiontype.get('cid')
                if ptype == '12166':
                    g.add((self.uri, CONVERIS.pubCardId, Literal(card.cid)))
                    continue
            except AttributeError:
                pass
            g += converis.to_graph(card, Position)
            g.add((self.uri, VIVO.relatedBy, card_uri(card.cid)))
        return g

    def _label(self):
        l = "{}, {}".format(self.cffamilynames, self.cffirstnames)
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
            p.set(VIVO.orcidId, self.orcid_uri)
            # Confirm the orcid
            g.add((self.orcid_uri, RDF.type, OWL.Thing))
            # Todo - review if we want to confirm all orcids
            g.add((self.orcid_uri, VIVO.confirmedOrcidId, self.uri))

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

        # positions
        g += self.get_positions()

        return g

    def _vcard_name(self):
        g = Graph()
        vc = Resource(g, URIRef(self.vcard_name_uri))
        vc.set(RDF.type, VCARD.Name)
        vc.set(RDFS.label, Literal(self._label()))
        vc.set(VCARD.familyName, Literal(self.cffamilynames))
        vc.set(VCARD.givenName, Literal(self.cffirstnames))
        if hasattr(self, 'middlename'):
            vc.set(VIVO.middleName, Literal(self.middlename))
        return g

    def _vcard_title(self):
        if not hasattr(self, 'academictitle'):
            return None
        g = Graph()
        vt = Resource(g, self.vcard_title_uri)
        vt.set(RDF.type, VCARD.Title)
        vt.set(RDFS.label, Literal(self.academictitle))
        vt.set(VCARD.title, Literal(self.academictitle))
        return g

    def _vcard_email(self):
        if not hasattr(self, 'email'):
            return None
        g = Graph()
        vt = Resource(g, self.vcard_email_uri)
        vt.set(RDF.type, VCARD.Email)
        # Label probably not necessary
        vt.set(RDFS.label, Literal(self.email))
        vt.set(VCARD.email, Literal(self.email))
        return g


class Position(BaseModel):

    def _date(self, dtype, dv):
        g = Graph()
        date_obj = converis.convert_date(dv)
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


    def to_rdf(self):
        g = Graph()
        e = Resource(g, self.uri)
        e.set(RDF.type, VIVO.Position)
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
        return g


class Organization(BaseModel):


    def related_uri(self, c_id):
        return D['c' + c_id]

    def get_children(self):
        """
        Get sub-organizations.
        """
        out = []
        for org in converis.get_related_ids("Organisation", self.cid, "ORGA_has_child_ORGA"):
            out.append(self.related_uri(org))
        return out

    def get_positions(self):
        g = Graph()
        # skip these orgs
        if self.cid in ['494698', '494815']:
            return g
        for card in converis.get_related_ids('Card', self.cid, 'CARD_has_ORGA'):
            g.add((self.uri, VIVO.relatedBy, card_uri(card)))
        return g

    def get_url(self):
        FHD = Namespace('http://vivo.fredhutch.org/ontology/display#')
        g = Graph()
        try:
            if self.cfuri is not None:
                g.add((self.uri, FHD.url, Literal(self.cfuri)))
            return g
        except AttributeError:
            return g

    def get_type(self):
        FHD = Namespace('http://vivo.fredhutch.org/ontology/display#')
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
        otype = self.typeoforga['cid']
        oty = m.get(otype, FHD.Organization)
        return oty


    def to_rdf(self):
        g = Graph()
        o = Resource(g, self.uri)
        o.set(RDF.type, self.get_type())
        o.set(RDFS.label, Literal(self.cfname))
        o.set(CONVERIS.converisId, Literal(self.cid))
        if hasattr(self, 'cfresact'):
            o.set(VIVO.overview, Literal(self.cfresact))
        for child in self.get_children():
            # Has sub-organization
            o.set(OBO['BFO_0000051'], child)
        # Get positions for this org.
        g += self.get_positions()

        g += self.get_url()
        return g


class Concept(BaseModel):
    """
    Handle research areas or concepts.
    """

    def to_rdf(self):
        g = Graph()
        r = Resource(g, self.uri)
        r.set(RDF.type, SKOS.Concept)
        r.set(RDFS.label, Literal(self.name))
        r.set(CONVERIS.converisId, Literal(self.cid))
        return g


class Publication(BaseModel):

    def get_type(self, default=BIBO.Document):
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
        if hasattr(self, 'publicationtype'):
            ctype = self.publicationtype['value'].strip()
            return ptypes.get(ctype, BIBO.Article)
        return default

    def data_properties(self):
        props = [
            ('srcauthors', CONVERIS.authorList),
            ('doi', BIBO.doi),
            ('pmid', BIBO.pmid),
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
        for card in converis.get_related_ids('Card', self.cid, 'PUBL_has_CARD'):
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


class Area(BaseModel):

    def has_researchers(self):
        g = Graph()
        for person in converis.get_related_ids('Person', self.cid, 'PERS_has_AREA'):
            puri = person_uri(person)
            g.add((self.uri, VIVO.researchAreaOf, puri))
        return g

    def get_narrower(self):
        g = Graph()
        for area in converis.get_related_ids('Area', self.cid, 'AREA_has_child_AREA'):
            narrow = area_uri(area)
            g.add((self.uri, SKOS.narrower, norrow))
        return g
  
    def to_rdf(self):
        g = Graph()
        r = Resource(g, self.uri)
        r.set(RDF.type, SKOS.Concept)
        r.set(RDFS.label, Literal(self.name))
        r.set(CONVERIS.converisId, Literal(self.cid))

        g += self.has_researchers()
        g += self.get_narrower()

        return g

def pub_to_card(card_id):
    g = Graph()
    for pub in converis.get_related_ids('Publication', card_id, 'PUBL_has_CARD'):
        #ashipuri = D['aship-{}-{}'.format(pub, self.cid)]
        puri = pub_uri(pub)
        g.add((puri, CONVERIS.pubCardId, Literal(card_id)))
    return g
