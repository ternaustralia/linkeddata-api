from typing import Optional

from linkeddata_api import data
from linkeddata_api.domain import schema


def get_optional_value(row: dict, key: str) -> Optional[str]:
    return row.get(key)["value"] if row.get(key) else None


def get(
    sparql_endpoint: str = "https://graphdb.tern.org.au/repositories/dawe_vocabs_core",
) -> schema.Item:
    """Get

    Raises RequestError and SPARQLResultJSONError
    """

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
        FROM <https://linked.data.gov.au/def/nrm>
        WHERE { 
            <https://linked.data.gov.au/def/nrm> dcterms:hasPart ?uri .
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

    result = data.sparql.post(query, sparql_endpoint).json()

    vocabs = []

    try:
        for row in result["results"]["bindings"]:
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
        raise data.exceptions.SPARQLResultJSONError(
            f"Unexpected SPARQL result set.\n{result}\n{err}"
        ) from err

    return vocabs
