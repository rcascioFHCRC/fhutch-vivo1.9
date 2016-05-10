"""
This is placeholder script just to get images working from Converis to VIVO.
We will need something different.
"""

import csv
import os
import sys

# Chemistry CMS client 
# https://github.com/apache/chemistry-cmislib
from cmislib import CmisClient

from rdflib import Graph, Literal

from converis import backend

from models import FHD
from models import person_uri

class ConverisDocs(object):
    def __init__(self, image_path):
        client = CmisClient(
            os.environ['CONVERIS_CHEMISTRY'],
            os.environ['CONVERIS_USER'],
            os.environ['CONVERIS_PASS']
        )
        self.repo = client.defaultRepository
        self.path = image_path

    def save_pic(self, person_id, pic_id):
        doc = self.repo.getObject(pic_id)
        stream = doc.getContentStream()
        fname = "{}.jpg".format(person_id)
        full_path = os.path.join(self.path, fname)
        with open(full_path, 'wb') as of:
            of.write(stream.read())
        return fname

def pic_statements(pics_added):
    g = Graph()
    for person_id, url in pics_added:
        puri = person_uri(person_id)
        g.add((puri, FHD.image, Literal(url)))
    return g


def harvest_people(sample=False):
    p = get_people(sample=sample)
    #print p.serialize(format='n3')
    


if __name__ == "__main__":
    infile = sys.argv[1]
    img_dir = sys.argv[2]
    url_base = os.environ['PHOTO_BASE_URL']
    pics_added = []
    with open(infile) as inf:
        for row in csv.DictReader(inf):
            pid = row['person']
            cid = row['pic_id']
            print>>sys.stderr, "Fetching photo", pid
            cd = ConverisDocs(img_dir)
            fname = cd.save_pic(pid, cid)
            url = url_base + fname
            pics_added.append((pid, url))
    
    g = pic_statements(pics_added)
    
    #print g.serialize(format="turtle")
    backend.sync_updates("http://localhost/data/photos", g)