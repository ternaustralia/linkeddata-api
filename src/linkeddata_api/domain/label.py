from typing import Union

from jinja2 import Template

from linkeddata_api import data


def get(
    uri: str,
    sparql_endpoint: str,
) -> Union[str, None]:
    """
    Returns a label or None if no label found.
    """
    # TODO: Currently, we try and fetch from TERN's controlled vocabularies.
    # We may want to also fetch with a SERVICE query from other repositories in the future.
    template = Template(
        """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <https://schema.org/>
        PREFIX sdo: <http://schema.org/>

        SELECT DISTINCT ?label
        WHERE {
            {
                BIND(<{{ uri }}> as ?uri)
                VALUES (?labelProperty) {
                    (skos:prefLabel)
                    (rdfs:label)
                    (dcterms:title)
                    (schema:name)
                    (sdo:name)
                    (dcterms:identifier)
                }
                ?uri ?labelProperty ?label .
            }
            {% if uri.startswith('http://linked.data.gov.au/def/tern-cv/') %}
            UNION {
                SERVICE <https://graphdb.tern.org.au/repositories/tern_vocabs_core> {
                    BIND(<{{ uri }}> as ?uri)
                    VALUES (?labelProperty) {
                        (skos:prefLabel)
                        (rdfs:label)
                        (dcterms:title)
                        (schema:name)
                        (sdo:name)
                        (dcterms:identifier)
                    }
                    ?uri ?labelProperty ?label .
                }
            }
            {% endif %}
        }
        LIMIT 1
    """
    )
    query = template.render(uri=uri)

    result = data.sparql.post(query, sparql_endpoint).json()

    try:
        rows = result["results"]["bindings"]
        for row in rows:
            return row["label"]["value"]
    except KeyError as err:
        raise data.exceptions.SPARQLResultJSONError(
            f"Unexpected SPARQL result set.\n{result}\n{err}"
        ) from err


def _get_from_list_query(uris: list[str]) -> str:
    # TODO: Currently, we try and fetch from TERN's controlled vocabularies.
    # We may want to also fetch with a SERVICE query from other repositories in the future.
    template = Template(
        """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <https://schema.org/>
        PREFIX sdo: <http://schema.org/>

        SELECT DISTINCT ?uri ?label
        WHERE {
            {% for uri in uris %}
            {
                SELECT DISTINCT ?uri ?label
                WHERE {
                    {
                        BIND(<{{ uri }}> as ?uri)
                        VALUES (?labelProperty) {
                            (skos:prefLabel)
                            (rdfs:label)
                            (dcterms:title)
                            (schema:name)
                            (sdo:name)
                            (dcterms:identifier)
                        }
                        ?uri ?labelProperty ?label .
                    }
                    {% if uri.startswith('http://linked.data.gov.au/def/tern-cv/') %}
                    UNION {
                        SERVICE <https://graphdb.tern.org.au/repositories/tern_vocabs_core> {
                            BIND(<{{ uri }}> as ?uri)
                            VALUES (?labelProperty) {
                                (skos:prefLabel)
                                (rdfs:label)
                                (dcterms:title)
                                (schema:name)
                                (sdo:name)
                                (dcterms:identifier)
                            }
                            ?uri ?labelProperty ?label .
                        }
                    }
                    {% endif %}
                }
                LIMIT 1
            }
            {% if not loop.last %}UNION{% endif %}
            {% endfor %}
        }
    """
    )
    query = template.render(uris=uris)
    return query


def get_from_list(
    uris: list[str],
    sparql_endpoint: str,
) -> dict[str, str]:
    """Returns a dict of uri keys and label values.

    In addition to the SPARQL endpoint provided, it also fetches labels
    from TERN's controlled vocabularies via a federated SPARQL query.
    """
    query = _get_from_list_query(uris)

    result = data.sparql.post(query, sparql_endpoint).json()

    labels = {}

    try:
        rows = result["results"]["bindings"]
        for row in rows:
            uri = str(row["uri"]["value"])
            label = str(row["label"]["value"])
            labels[uri] = label

    except KeyError as err:
        if result["results"]["bindings"] == [{}]:
            return {}

        raise data.exceptions.SPARQLResultJSONError(
            f"Unexpected SPARQL result set.\n{result}\n{err}"
        ) from err

    return labels
