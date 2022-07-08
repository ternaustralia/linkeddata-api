from typing import Union

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
