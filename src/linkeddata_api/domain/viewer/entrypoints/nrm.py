from jinja2 import Template

from linkeddata_api import data
from linkeddata_api.domain import schema
from linkeddata_api.domain.viewer.entrypoints.utils import (
    ceiling_division,
    get_optional_value,
)


def get_count(sparql_endpoint: str) -> int:
    query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX reg: <http://purl.org/linked-data/registry/>
        SELECT (COUNT(*) AS ?count)
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

            FILTER NOT EXISTS {
                ?uri owl:deprecated true .
            }
        }
    """

    result = data.sparql.post(query, sparql_endpoint).json()

    return int(result["results"]["bindings"][0]["count"]["value"])


def get(
    sparql_endpoint: str,
    page: int,
) -> schema.EntrypointItems:
    """Get

    Raises RequestError and SPARQLResultJSONError
    """
    limit = 20

    query = Template(
        """
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
        LIMIT {{ limit }}
        OFFSET {{ offset }}
    """
    ).render(limit=20, offset=(page - 1) * limit)

    result = data.sparql.post(query, sparql_endpoint).json()

    count = get_count(sparql_endpoint)
    more_pages_exist = False
    if count > (page * limit):
        more_pages_exist = True

    total_pages = ceiling_division(count, limit)

    vocabs = []

    for row in result["results"]["bindings"]:
        vocabs.append(
            schema.EntrypointItem(
                id=str(row["uri"]["value"]),
                label=str(row["label"]["value"]),
                description=get_optional_value(row, "description"),
                created=get_optional_value(row, "created"),
                modified=get_optional_value(row, "modified"),
            )
        )

    return schema.EntrypointItems(
        items=vocabs,
        more_pages_exists=more_pages_exist,
        items_count=count,
        limit=limit,
        total_pages=total_pages,
    )
