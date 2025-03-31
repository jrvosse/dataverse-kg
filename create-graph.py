#! /usr/bin/env python
# coding: UTF-8
import requests
import xmltodict
import re
import logging
import argparse
from config import DATAVERSE_URL, FUSEKI_URL, FUSEKI_COLLECTION, FUSEKI_LOGIN, FUSEKI_PASSWORD, DEBUG
from utils import resolve_blank_nodes
from rdflib import Graph
from urllib.parse import urlparse

logging.basicConfig(filename='./dv2fuseki.log', level=logging.DEBUG)

def uploadRDF(lasturl, bnode_url, logger):
    response = requests.get(lasturl)
    logger.info("uploadRDF(%s)"%lasturl)
    # print(json.loads(response.text))
    uploadfusekiurl = "%s/%s/data" % (FUSEKI_URL, FUSEKI_COLLECTION)
    g = Graph()
    g.parse(data=response.text, format="json-ld")
    # Resolve blank nodes
    resolved_graph = resolve_blank_nodes(bnode_url, g, logger)
    json_ser = resolved_graph.serialize(format="json-ld").encode('utf8')
    resp = requests.post(uploadfusekiurl, data=json_ser,
                         auth=(FUSEKI_LOGIN, FUSEKI_PASSWORD),
                         headers={"Content-Type": "application/ld+json; charset=utf8"})
    logger.debug(resp.text)
    return

def get_items(doc, bnode_url, logger):
    for item in doc['urlset']['url']:
        hostitems = re.search(r"^(\S+)\/dataset\S+\?(persistent\S+)$", item['loc'])
        if hostitems:
            dvnurl = "%s/api/datasets/export?exporter=OAI_ORE&%s" % (
            DATAVERSE_URL, hostitems.group(2))
            # print(dvnurl)
            uploadRDF(dvnurl, bnode_url, logger)
            # except: print("UploadRDF() failed, Ignore %s" % dvnurl)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( '-log',
                     '--loglevel',
                     default='info',
                     help='Provide logging level. Example --loglevel debug, default=info' )
    args = parser.parse_args()
    logging.basicConfig( level=args.loglevel.upper() )
   
    url = f"{DATAVERSE_URL}/sitemap.xml"
    parsed_url = urlparse(url)
    bnode_url = f"{parsed_url.scheme}://{parsed_url.netloc}/bnode"
    response = requests.get(url)
    doc = xmltodict.parse(response.text)
    logger = logging.getLogger(__name__)
    logger.info(url)
    logger.debug(response.text)

    get_items(doc, bnode_url, logger)

if __name__ == '__main__':
    main()