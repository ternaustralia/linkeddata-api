from rdflib import Graph


def create_graph() -> Graph:
    """Create a new RDFLib Graph object with opinionated namespace prefix bindings."""
    graph = Graph()
    graph.bind("tern", "https://w3id.org/tern/ontologies/tern/")
    return graph
