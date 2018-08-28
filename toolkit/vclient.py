"""
VIVO client for adding and removing triples from API
without using SPARQL.
"""
import os

import logging
logger = logging.getLogger("converis_client")

import requests


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
    rsp = requests.post(url, data=dict(email=user, password=password, update=msg), verify=False)
    if rsp.status_code != 200:
        logger.error(rsp.text)
        raise Exception("Update failed to {}.".format(named_graph))
    return True


def add(named_graph, graph):
    return _direct(named_graph, graph)


def delete(named_graph, graph):
    return _direct(named_graph, graph, add=False)
