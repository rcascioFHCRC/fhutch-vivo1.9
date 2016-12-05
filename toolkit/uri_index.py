"""
Build indexes for URI creation.
"""
import logging
import os
import pickle
import sys

from converis import client

import log_setup

logger = log_setup.get_logger()

if os.environ.get('HTTP_CACHE') == "1":
  import requests_cache
  requests_cache.install_cache(
     'converis',
     backend='redis',
     allowable_methods=('GET', 'PUT'))


def build_short_url_index():
    query = """
    <data xmlns="http://converis/ns/webservice">
     <return>
      <attributes>
        <attribute name="shortURL"/>
       </attributes>
     </return>
     <query>
      <filter for="Person" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
        <and>
          <attribute operator="notequals" argument="" name="shortURL"/>
        </and>
      </filter>
     </query>
    </data>
    """
    d = {}
    for item in client.filter_query(query):
        d[item.cid] = item.shorturl
    with open('data/people.idx', 'wb') as of:
        pickle.dump(d, of)


if __name__ == "__main__":
	logger.info("Build URI indexes")
	build_short_url_index()