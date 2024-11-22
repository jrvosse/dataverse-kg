# Dataverse Knowledge Graph ingest 

Quick start:
```
pip3 install -r requirements.txt
cp config-init.py config.py
```
Fill configuration variables and start ingest:
```
python3 ./create-graph.py
```
Warning: Ingest of 10k datasets from Dataverse in Jena Fuseki will take in average about one hour.
