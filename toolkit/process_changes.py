"""
Command-line script for comparing RDF from one update
to the next and saving RDF files of additions and removals
to the staging directory.

Also posts additions and removals.

"""

import glob
import os
import time

from rdflib import Graph
from rdflib.compare import graph_diff

import vclient
import log_setup

logger = log_setup.get_logger()

current_path = os.path.join('data', 'current')
previous_path = os.path.join('data', 'last')
staging_path = os.path.join('data', 'staged')
add_path = os.path.join(staging_path, 'add')
remove_path = os.path.join(staging_path, 'delete')

ng_base = "http://localhost/data/"


def do_diff():
    logger.info("Diffing updates")

    for triple_file in glob.glob(os.path.join(current_path, '*.nt')):
        current_g = Graph().parse(triple_file, format="nt")
        logger.info("Processing {}. Found {} incoming triples.".format(triple_file, len(current_g)))
        fn = os.path.split(triple_file)[-1]
        last_file = os.path.join(previous_path, fn)
        if os.path.exists(last_file) is True:
            last_g = Graph().parse(last_file, format="nt")
            logger.info("Processing {}. Found {} incoming triples.".format(last_file, len(last_g)))
        else:
            last_g = Graph()

        both, adds, deletes = graph_diff(current_g, last_g)
        del both

        add_out = os.path.join(add_path, fn)
        logger.info("Serializing {} adds to {}.".format(len(adds), add_out))
        remove_out = os.path.join(remove_path, fn)
        adds.serialize(destination=add_out, format="nt")
        logger.info("Serializing {} deletes to {}.".format(len(deletes), remove_out))
        deletes.serialize(destination=remove_out, format="nt")

    return True


def post_updates():
    # Adds
    for afile in glob.glob(add_path + "/*"):
        etype = os.path.basename(afile).split('.')[0]
        ng = ng_base + etype
        g = Graph()
        g.parse(source=afile, format="nt")
        logger.info("Adding {} triples to {}.".format(len(g), ng))
        vclient.add(ng, g)
        time.sleep(2)

    # Deletes
    for dfile in glob.glob(remove_path + "/*"):
        etype = os.path.basename(afile).split('.')[0]
        ng = ng_base + etype
        g = Graph()
        g.parse(source=afile, format="nt")
        logger.info("Removing {} triples to {}.".format(len(g), ng))
        vclient.delete(ng, g)
        time.sleep(2)

    logger.info("Sync finished")


def main():
    do_diff()
    post_updates()


if __name__ == "__main__":
    main()
