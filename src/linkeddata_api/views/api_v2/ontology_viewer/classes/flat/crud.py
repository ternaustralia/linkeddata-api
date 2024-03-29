from typing import List

import requests
from jinja2 import Template
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response
from flask_tern.cache import cache

from . import schema


ontology_id_mapping = {
    "tern-ontology": {
        "sparql_endpoint": "https://graphdb.tern.org.au/repositories/knowledge_graph_core",
        "named_graph": "https://w3id.org/tern/ontologies/tern/",
    }
}


query_template = Template(
    """
# Get a list of classes ordered by label.
#   Only one string or langString of type "en" is retrieved as label.

PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT distinct ?id (SAMPLE(?_label) as ?label)
FROM <http://www.ontotext.com/explicit>
FROM <{{ named_graph }}>
WHERE {
    {
        ?_class a sh:NodeShape .
        ?_class sh:targetClass ?id .

        FILTER(!isBlank(?id))

        {
            ?id rdfs:label ?_label .
        }
        UNION {
            ?id skos:prefLabel ?_label .
        }
    }
}
GROUP BY ?id
ORDER BY ?label
"""
)


@cache.memoize()
def get(ontology_id: str) -> List[schema.ClassItem]:
    try:
        mapping = ontology_id_mapping[ontology_id]
    except KeyError as err:
        description = f"Unknown ontology ID '{ontology_id}'. Valid ontology IDs: {list(ontology_id_mapping.keys())}"
        raise HTTPException(
            description=description, response=Response(description, status=404)
        ) from err

    query = query_template.render(named_graph=mapping["named_graph"])
    headers = {
        "accept": "application/sparql-results+json",
        "content-type": "application/sparql-query",
    }

    r = requests.post(
        url=mapping["sparql_endpoint"], headers=headers, data=query, timeout=60
    )

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise HTTPException(
            description=err.response.text,
            response=Response(err.response.text, status=502),
        ) from err

    resultset = r.json()
    classes = []
    for row in resultset["results"]["bindings"]:
        classes.append(
            schema.ClassItem(id=row["id"]["value"], label=row["label"]["value"])
        )

    return classes
