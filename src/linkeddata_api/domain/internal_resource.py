from jinja2 import Template

from linkeddata_api import data


def _get_from_list_query(uris: list[str]) -> str:
    template = Template(
        """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT distinct ?uri ?internal
        WHERE {
            VALUES (?uri) {
                {% for uri in uris %}
                (<{{ uri }}>)
                {% endfor %}
            }
            
            bind(exists{ ?uri ?p ?o } as ?internal)
        }
    """
    )
    return template.render(uris=uris)


def get_from_list(
    uris: list[str],
    sparql_endpoint: str,
) -> dict[str, str]:
    query = _get_from_list_query(uris)

    result = data.sparql.post(query, sparql_endpoint).json()

    return_results = {}

    try:
        rows = result["results"]["bindings"]
        for row in rows:
            uri = str(row["uri"]["value"])
            internal = str(row["internal"]["value"])
            return_results[uri] = True if internal == "true" else False

    except KeyError as err:
        raise data.exceptions.SPARQLResultJSONError(
            f"Unexpected SPARQL result set.\n{result}\n{err}"
        ) from err

    return return_results
