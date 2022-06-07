from typing import Optional

import requests
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response

from . import schema
from .. import settings


def get_optional_value(row: dict, key: str) -> Optional[str]:
    return row.get(key)["value"] if row.get(key) else None


def get() -> schema.Item:
    query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX reg: <http://purl.org/linked-data/registry/>
        SELECT 
        ?uri 
        (SAMPLE(?_label) as ?label) 
        (SAMPLE(?_description) as ?description) 
        (SAMPLE(?_created) as ?created)
        (SAMPLE(?_modified) as ?modified)
        FROM <http://www.ontotext.com/explicit>
        FROM <https://linked.data.gov.au/def/test/dawe-cv/>
        WHERE { 
            ?uri reg:register <https://linked.data.gov.au/def/test/dawe-cv/616c7c18-3309-472d-a38d-8106a1b6ff9b> .
            VALUES (?vocabularyType) {
                (skos:ConceptScheme)
                (skos:Collection)
            }
            ?uri a ?vocabularyType ;
                skos:prefLabel ?_label .

            OPTIONAL { ?uri dcterms:description ?_description }
            OPTIONAL { ?uri dcterms:created ?_created }
            OPTIONAL { ?uri dcterms:modified ?_modified }
        }
        GROUP by ?uri
        ORDER by ?label 
    """

    headers = {
        "accept": "application/sparql-results+json",
        "content-type": "application/sparql-query",
    }

    r = requests.post(url=settings.SPARQL_ENDPOINT, headers=headers, data=query)

    try:
        r.raise_for_status()
    except requests.RequestException as err:
        raise HTTPException(
            description=err.response.text,
            response=Response(err.response.text, status=502),
        ) from err

    resultset = r.json()
    vocabs = []

    try:
        for row in resultset["results"]["bindings"]:
            vocabs.append(
                schema.Item(
                    id=str(row["uri"]["value"]),
                    label=str(row["label"]["value"]),
                    description=get_optional_value(row, "description"),
                    created=get_optional_value(row, "created"),
                    modified=get_optional_value(row, "modified"),
                )
            )
    except KeyError as err:
        raise HTTPException(
            description=r.text,
            response=Response("Unexpected SPARQL result set.\n" + str(err), status=502),
        ) from err

    return vocabs
