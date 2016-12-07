"""
Build indexes for URI creation.
"""
import logging
import os
import pickle
import re
import sys

from converis import client

import log_setup

logger = log_setup.get_logger()

SHORT_URLS = "data/uris.idx"

if os.environ.get('HTTP_CACHE') == "1":
  import requests_cache
  requests_cache.install_cache(
     'converis',
     backend='redis',
     allowable_methods=('GET', 'PUT'))

SLUG_REGEX = re.compile('^[-\w]+$')

def validate_slug(raw):
	"""
	Add basic validation to the incoming shortURLs. 
	- no empty strings
	- minimum of 3 characters
	- only 
	"""
	if raw == "":
		return False
	elif len(raw) < 3:
		return False
	if re.match(SLUG_REGEX, raw) is not None:
		return True
	return False


def build_short_url_index():
	logger.info("Building people shortURL index.")
	people_query = """
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
	for item in client.filter_query(people_query):
		if validate_slug(item.shorturl) is False:
			logger.info("{} - {} is not a valid shortURL.".format(item.cid, item.shorturl))
			continue
		d[item.cid] = item.shorturl
	logger.info("Building org shortURL index.")
	# orgs too
	org_query = """
	<data xmlns="http://converis/ns/webservice">
	<return>
	<attributes>
	<attribute name="shortURL"/>
	</attributes>
	</return>
	<query>
	<filter for="Organisation" xmlns="http://converis/ns/filterengine" xmlns:sort="http://converis/ns/sortingengine">
	<and>
	  <attribute operator="notequals" argument="" name="shortURL"/>
	</and>
	</filter>
	</query>
	</data>
	"""
	for item in client.filter_query(org_query):
		if validate_slug(item.shorturl) is False:
			logger.info("{} - {} is not a valid shortURL.".format(item.cid, item.shorturl))
			continue
		d[item.cid] = item.shorturl
	# write to disk
	with open(SHORT_URLS, 'w+') as of:
		pickle.dump(d, of)


if __name__ == "__main__":
	logger.info("Build URL indexes")
	build_short_url_index()
	logger.info("Short URL index complete.")