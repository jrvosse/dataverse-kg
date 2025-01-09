# coding: UTF-8
import requests
import xmltodict
import json
import pprint
import re
from config import DATAVERSE_URL, FUSEKI_URL, FUSEKI_COLLECTION, FUSEKI_LOGIN, FUSEKI_PASSWORD, DEBUG
from utils import resolve_blank_nodes
from rdflib import Graph
from urllib.parse import urlparse

url = f"{DATAVERSE_URL}/sitemap.xml"
parsed_url = urlparse(url)
bnode_url = f"{parsed_url.scheme}://{parsed_url.netloc}/bnode"
response = requests.get(url)
doc = xmltodict.parse(response.text)
pp = pprint.PrettyPrinter(indent=4)

def uploadRDF(lasturl):
    response = requests.get(lasturl)
    print("uploadRDF(%s)"%lasturl)
    # print(json.loads(response.text))
    uploadfusekiurl = "%s/%s/data" % (FUSEKI_URL, FUSEKI_COLLECTION)
    g = Graph()
    g.parse(data=response.text, format="json-ld")
    # Resolve blank nodes
    resolved_graph = resolve_blank_nodes(bnode_url, g)
    json_ser = resolved_graph.serialize(format="json-ld").encode('utf8')
    resp = requests.post(uploadfusekiurl, data=json_ser,
                         auth=(FUSEKI_LOGIN, FUSEKI_PASSWORD),
                         headers={"Content-Type": "application/ld+json; charset=utf8"})
    if DEBUG:
        print(resp.text)
    return


for item in doc['urlset']['url']:
    hostitems = re.search("^(\S+)\/dataset\S+\?(persistent\S+)$", item['loc'])
    if hostitems:
        dvnurl = "%s/api/datasets/export?exporter=OAI_ORE&%s" % (
        hostitems.group(1), hostitems.group(2))
        # print(dvnurl)
        uploadRDF(dvnurl)
        # except: print("UploadRDF() failed, Ignore %s" % dvnurl)
