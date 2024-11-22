from rdflib import Graph, URIRef, Literal, BNode
from urllib.parse import urlparse

def resolve_blank_nodes(bnode_url, graph):
    """
    Resolves blank nodes in an RDF graph by converting them to URIs and preserving their properties.
    
    Args:
        bnode_url (str): Base URL to use for generating new URIs for blank nodes
        graph (rdflib.Graph): Input RDF graph containing blank nodes
        
    Returns:
        rdflib.Graph: New graph with resolved blank nodes
    """
    resolved_graph = Graph()
    for subj, pred, obj in graph:
        if isinstance(obj, BNode):
            # Retrieve properties attached to the blank node
            attached_data = {p: o for s, p, o in graph.triples((obj, None, None))}
            # Generate a unique URI for the blank node based on its attached properties
            new_uri = URIRef(f"{bnode_url}/{hash(obj)}")
            # Add the original triple with the new URI
            resolved_graph.add((subj, pred, new_uri))
            # Add the attached properties to the graph using the new URI
            for p, o in attached_data.items():
                # Convert string URLs to URIRef in attached data
                if isinstance(o, Literal) and ('http://' in str(o) or 'https://' in str(o)):
                    o = URIRef(str(o))
                if isinstance(p, Literal) and ('http://' in str(p) or 'https://' in str(p)):
                    p = URIRef(str(p))
                resolved_graph.add((new_uri, p, o))
        else:
            # Convert string URLs to URIRef for non-blank node objects and predicates
            if isinstance(obj, Literal) and ('http://' in str(obj) or 'https://' in str(obj)):
                obj = URIRef(str(obj))
            if isinstance(pred, Literal) and ('http://' in str(pred) or 'https://' in str(pred)):
                pred = URIRef(str(pred))
            resolved_graph.add((subj, pred, obj))
    return resolved_graph 