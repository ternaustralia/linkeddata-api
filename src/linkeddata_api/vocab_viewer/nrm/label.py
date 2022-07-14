from typing import Union

from jinja2 import Template

from linkeddata_api.vocab_viewer import nrm


def get(
    uri: str,
    sparql_endpoint: str = "https://graphdb.tern.org.au/repositories/dawe_vocabs_core",
) -> Union[str, None]:
    """
    Returns a label or None if no label found.
    """
    query = f"""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT DISTINCT ?label
        WHERE {{
            VALUES (?labelProperty) {{
                (skos:prefLabel)
            }}
            <{uri}> ?labelProperty ?label .
        }}
    """

    result = nrm.sparql.post(query, sparql_endpoint)

    try:
        rows = result["results"]["bindings"]
        for row in rows:
            return row["label"]["value"]
    except KeyError as err:
        raise nrm.exceptions.SPARQLResultJSONError(
            f"Unexpected SPARQL result set.\n{result}\n{err}"
        ) from err


def _get_from_list_query(uris: list[str]) -> str:
    # TODO: Currently, we try and fetch from TERN's controlled vocabularies.
    # We may want to also fetch with a SERVICE query from other repositories in the future.
    template = Template(
        """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT DISTINCT ?uri (SAMPLE(?_label) AS ?label)
        WHERE {
            VALUES (?uri) {
                {% for uri in uris %}
                (<{{ uri }}>)
                {% endfor %}
            }
            
            {
                ?uri skos:prefLabel ?_label .        
            }
            UNION {
                # Also try and fetch label from TERN's controlled vocabularies.
                SERVICE <https://graphdb.tern.org.au/repositories/tern_vocabs_core> {
                    ?uri skos:prefLabel ?_label .
                }
            }
        }
        GROUP BY ?uri
    """
    )
    return template.render(uris=uris)


def get_from_list(
    uris: list[str],
    sparql_endpoint: str = "https://graphdb.tern.org.au/repositories/dawe_vocabs_core",
) -> dict[str, str]:
    """Returns a dict of uri keys and label values.

    In addition to the SPARQL endpoint provided, it also fetches labels
    from TERN's controlled vocabularies via a federated SPARQL query.
    """
    query = _get_from_list_query(uris)

    result = nrm.sparql.post(query, sparql_endpoint)

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

        raise nrm.exceptions.SPARQLResultJSONError(
            f"Unexpected SPARQL result set.\n{result}\n{err}"
        ) from err

    return labels
