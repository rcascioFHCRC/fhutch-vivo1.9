import os

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.query import ResultException
from rdflib.compare import graph_diff

from vstore import VIVOUpdateStore

from namespaces import rq_prefixes, VIVO

import logging
logger = logging.getLogger("converis_client")

# library's default is 8000
BATCH_SIZE = 4000

class SyncVStore(VIVOUpdateStore):
    """
    Extending VIVOUpdateStore with utilities
    for syncing data to named graphs.
    """

    def ng_construct(self, named_graph, rq):
        """
        Run construct query against a named graph.
        """
        ng = URIRef(named_graph)
        query = rq
        try:
            rsp = self.query(
                query,
                initBindings=dict(g=ng),
            )
            return rsp.graph
        except ResultException:
            return Graph()


    def get_existing(self, named_graph):
        """
        Get existing triples from a named graph.
        """
        # SPARQL query to fetch existing data.
        rq = """
        CONSTRUCT {?s ?p ?o }
        WHERE { GRAPH ?g {?s ?p ?o } }
        """
        return self.ng_construct(named_graph, rq)


    def sync_named_graph(self, name, incoming):
        """
        Pass in incoming data and sync with existing data in
        named graph.
        """
        existing = self.get_existing(name)
        both, adds, deletes = graph_diff(incoming, existing)
        del both
        added = self.bulk_add(name, adds, size=BATCH_SIZE)
        logger.info("Adding {} triples.".format(added))
        removed = self.bulk_remove(name, deletes, size=BATCH_SIZE)
	for sub in deletes.subjects():
	    logger.info("Removed {} from {}.".format(sub, name))
        logger.info("Removed {} triples.".format(removed))
        return (added, removed)


def post_updates(named_graph, graph):
    """
    Function for posting the data.
    """

    #Define the VIVO store
    query_endpoint = os.environ['VIVO_URL'] + '/api/sparqlQuery'
    update_endpoint = os.environ['VIVO_URL'] + '/api/sparqlUpdate'
    vstore = SyncVStore(
                os.environ['VIVO_EMAIL'],
                os.environ['VIVO_PASSWORD']
            )
    vstore.open((query_endpoint, update_endpoint))

    existing = vstore.get_existing(named_graph)

    # Get the URIs for statements that will be additions.
    changed_uris = set([u for u in graph.subjects()])

    # Get the statements from the deletes that apply to this
    # incremental update. This will be the posted deletes.
    remove_graph = Graph()
    # Remove all triples related to the changed uris.
    for curi in changed_uris:
        for pred, obj in existing.predicate_objects(subject=curi):
            remove_graph.add((curi, pred, obj))

    # Diff
    both, adds, deletes = graph_diff(graph, remove_graph)

    num_additions = len(adds)
    num_remove = len(deletes)

    if (num_additions == 0) and (num_remove == 0):
        logger.info("No updates to {}.".format(named_graph))
    else:
        #print adds.serialize(format='n3')
        #print '-' * 10
        #print deletes.serialize(format='n3')

        if num_additions > 0:
            logger.info("Will add {} triples to {}.".format(num_additions, named_graph))
            vstore.bulk_add(named_graph, adds)

        if num_remove > 0:
            logger.info("Will remove {} triples from {}.".format(num_remove, named_graph))
            vstore.bulk_remove(named_graph, deletes)

    return True


def sync_updates(named_graph, graph):
    """
    Function for posting the data.
    """

    #Define the VIVO store
    query_endpoint = os.environ['VIVO_URL'] + '/api/sparqlQuery'
    update_endpoint = os.environ['VIVO_URL'] + '/api/sparqlUpdate'
    vstore = SyncVStore(
                os.environ['VIVO_EMAIL'],
                os.environ['VIVO_PASSWORD']
            )
    vstore.open((query_endpoint, update_endpoint))
    vstore.sync_named_graph(named_graph, graph)
    return True


def get_store():
    """
    Connect to the raw store.
    """

    # Define the VIVO store
    query_endpoint = os.environ['VIVO_URL'] + '/api/sparqlQuery'
    update_endpoint = os.environ['VIVO_URL'] + '/api/sparqlUpdate'
    vstore = SyncVStore(
                os.environ['VIVO_EMAIL'],
                os.environ['VIVO_PASSWORD']
            )
    vstore.open((query_endpoint, update_endpoint))
    return vstore
