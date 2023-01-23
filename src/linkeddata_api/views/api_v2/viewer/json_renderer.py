from jinja2 import Template
from rdflib import RDF

from linkeddata_api import domain
from linkeddata_api.data import sparql
from linkeddata_api.data.exceptions import SPARQLNotFoundError

from .schema import URI, Resource, PredicateValues


def get_predicate_count_index(uri: str, predicate: str, sparql_endpoint: str) -> int:
    query = Template(
        """
        SELECT (COUNT(DISTINCT(?value)) as ?count)
        WHERE {
            <{{ uri }}> <{{ predicate }}> ?value .
        }
        """
    ).render(uri=uri, predicate=predicate)

    response = sparql.post(query, sparql_endpoint)

    count = int(response.json()["results"]["bindings"][0]["count"]["value"])
    return count


def get_predicate_values(
    uri: str, predicate: str, sparql_endpoint: str, limit: int, page: int
) -> PredicateValues:
    query = Template(
        """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?p ?o ?listItem ?listItemNumber (SAMPLE(?_label) AS ?label)
        WHERE {
            BIND(<{{ predicate }}> AS ?p)
            <{{ uri }}> ?p ?o .
            
            OPTIONAL{
                ?o skos:prefLabel ?_label .
            }
            
            BIND(EXISTS{?o rdf:rest ?rest} as ?listItem)

            # This gets set later with the listItemNumber value.
            BIND(0 AS ?listItemNumber)
        }
        GROUP BY ?p ?o ?listItem ?listItemNumber
        ORDER BY ?label
        LIMIT {{ limit }}
        OFFSET {{ offset }}
    """
    ).render(uri=uri, predicate=predicate, limit=limit, offset=(page - 1) * limit)

    count = get_predicate_count_index(uri, predicate, sparql_endpoint)

    response = sparql.post(query, sparql_endpoint)

    result = response.json()

    # An index of URIs with label values.
    uri_label_index = domain.viewer.resource.json.get_uri_label_index(
        result, sparql_endpoint
    )

    # An index of all the URIs linked to and from this resource that are available internally.
    uri_internal_index = domain.viewer.resource.json.get_uri_internal_index(
        result, sparql_endpoint
    )

    values = []

    for row in result["results"]["bindings"]:
        item = None

        if row["p"]["value"] == str(RDF.type):
            continue
        else:
            if row["o"]["type"] == "uri":
                # object_label = uri_label_index.get(
                #     row["o"]["value"]
                # ) or domain.curie.get(row["o"]["value"])
                object_label = (
                    uri_label_index.get(row["o"]["value"]) or row["o"]["value"]
                )
                item = domain.schema.URI(
                    label=object_label,
                    value=row["o"]["value"],
                    internal=uri_internal_index.get(row["o"]["value"], False),
                    list_item=True if row["listItem"]["value"] == "true" else False,
                    list_item_number=row["listItemNumber"]["value"]
                    if row["listItem"]["value"] == "true"
                    else None,
                )
            elif row["o"]["type"] == "literal":
                datatype = row["o"].get("datatype", "")
                if datatype:
                    datatype = domain.schema.URI(
                        label=datatype,
                        value=datatype,
                        internal=uri_internal_index.get(datatype, False),
                        list_item=True if row["listItem"]["value"] == "true" else False,
                        list_item_number=row["listItemNumber"]["value"]
                        if row["listItem"]["value"] == "true"
                        else None,
                    )
                else:
                    datatype = None

                item = domain.schema.Literal(
                    value=row["o"]["value"],
                    datatype=datatype,
                    language=row["o"].get("xml:lang", ""),
                    list_item=True if row["listItem"]["value"] == "true" else False,
                    list_item_number=row["listItemNumber"]["value"]
                    if row["listItem"]["value"] == "true"
                    else None,
                )
            elif row["o"]["type"] == "bnode":
                # TODO: Handle blank nodes.
                pass
            else:
                raise ValueError(
                    f"Expected type to be uri or literal but got {row['o']['type']}"
                )

            if item:
                values.append(item)

    predicate_values = PredicateValues(
        uri=uri, predicate=predicate, objects=values, count=count
    )
    return predicate_values.json()


def _get_predicates(uri: str, sparql_endpoint: str) -> list[URI]:
    query = Template(
        """
        SELECT DISTINCT ?p
        WHERE {
            <{{ uri }}> ?p ?o .
        }
        ORDER BY ?p
        """
    ).render(uri=uri)

    response = sparql.post(query, sparql_endpoint)

    predicates = [
        URI(
            label=domain.curie.get(row["p"]["value"]),
            value=row["p"]["value"],
            internal=False,
        )
        for row in response.json()["results"]["bindings"]
    ]

    return predicates


def _get_types(uri: str, sparql_endpoint: str) -> list[URI]:
    query = Template(
        """
        SELECT DISTINCT ?type
        WHERE {
            <{{ uri }}> a ?type .
            FILTER(!isBlank(?type))
        }
        ORDER BY ?type
        """
    ).render(uri=uri)

    response = sparql.post(query, sparql_endpoint)

    types = [
        URI(
            label=domain.label.get(row["type"]["value"], sparql_endpoint)
            or domain.curie.get(row["type"]["value"]),
            value=row["type"]["value"],
            internal=False,
        )
        for row in response.json()["results"]["bindings"]
    ]

    return types


def _exists(uri: str, sparql_endpoint: str) -> bool:
    query = Template(
        """
        ASK {
            <{{ uri }}> ?p ?o .
        }
        """
    ).render(uri=uri)

    response = sparql.post(query, sparql_endpoint)

    return response.json()["boolean"]


def json_renderer(uri: str, sparql_endpoint: str) -> Resource:
    if not _exists(uri, sparql_endpoint):
        raise SPARQLNotFoundError(f"Resource with URI {uri} not found.")

    label = domain.label.get(uri, sparql_endpoint)
    types = _get_types(uri, sparql_endpoint)
    predicates = _get_predicates(uri, sparql_endpoint)
    predicates = list(filter(lambda x: x.value != str(RDF.type), predicates))

    return Resource(uri=uri, label=label, types=types, properties=predicates).json()
