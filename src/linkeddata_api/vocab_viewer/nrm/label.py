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
    template = Template(
        """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT DISTINCT ?uri ?label
        WHERE {
            VALUES (?uri) {
                {% for uri in uris %}
                (<{{ uri }}>)
                {% endfor %}
            }
            
            ?uri skos:prefLabel ?label .
        }
    """
    )
    return template.render(uris=uris)


def get_from_list(
    uris: list[str],
    sparql_endpoint: str = "https://graphdb.tern.org.au/repositories/dawe_vocabs_core",
) -> dict[str, str]:
    """Returns a dict of uri keys and label values."""
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
        raise nrm.exceptions.SPARQLResultJSONError(
            f"Unexpected SPARQL result set.\n{result}\n{err}"
        ) from err

    return labels
