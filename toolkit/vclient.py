"""
VIVO client for adding and removing triples from API
without using SPARQL.
"""
from itertools import islice
import os

from rdflib import Graph
import requests

import logging
logger = logging.getLogger("converis_client")

SIZE = 3000


def make_batch(size, graph):
    """
    Split graphs into n sized chunks.
    See: http://stackoverflow.com/a/1915307/758157
    """
    tmpg = Graph()
    for n, trip in enumerate(graph):
        tmpg.add(trip)
        if (n > 0) and (n % size == 0):
            yield tmpg
            tmpg = Graph()
    yield tmpg


def _direct(named_graph, graph, add=True):
    if add is True:
        action = "INSERT"
    else:
        action = "DELETE"
    msg = """
    {action} DATA {{
       GRAPH <{ng}> {{
          {triples}
       }}
    }}
    """.format(**dict(action=action, ng=named_graph, triples=str(graph.serialize(format="nt"))))
    logger.info("Direct {} with {} triples to {}.".format(action, len(graph), named_graph))
    url = os.environ['VIVO_URL'] + '/api/sparqlUpdate'
    user = os.environ['VIVO_EMAIL']
    password = os.environ['VIVO_PASSWORD']
    rsp = requests.post(
        url,
        data=dict(email=user, password=password, update=msg),
        verify=False
    )
    if rsp.status_code != 200:
        logger.error(rsp.text)
        raise Exception("Update failed to {}.".format(named_graph))
    return True


def add(named_graph, graph):
    for grp in make_batch(SIZE, graph):
        logger.info("Adding batch to {} with {} triples.".format(named_graph, len(grp)))
        d = _direct(named_graph, grp)
    return d


def delete(named_graph, graph):
    for grp in make_batch(SIZE, graph):
        logger.info("Removing batch to {} with {} triples.".format(named_graph, len(grp)))
        d = _direct(named_graph, grp, add=False)
    return d
