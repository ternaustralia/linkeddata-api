from jinja2 import Template
from rdflib import RDF

from linkeddata_api import domain
from linkeddata_api.data import sparql
from linkeddata_api.data.exceptions import SPARQLNotFoundError

from .schema import URI, Resource, PredicateValues
from .profile.base_profile import get_profile


def predicate_is_list_item(uri: str, predicate: str, sparql_endpoint: str) -> bool:
    query = Template(
        """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        ASK {
            <{{ uri }}> <{{ predicate }}> ?o .
            ?o rdf:rest ?rest
        }
    """
    ).render(uri=uri, predicate=predicate)

    response = sparql.post(query, sparql_endpoint)
    data = response.json()

    return data["boolean"]


def get_predicate_count_index(uri: str, predicate: str, sparql_endpoint: str, profile: str) -> int:
    ProfileClass = get_profile(profile)

    if ProfileClass:
        profile_instance = ProfileClass(uri, [])
        count = profile_instance.get_predicate_values_count(predicate, sparql_endpoint)

    else:
        is_list_item = predicate_is_list_item(uri, predicate, sparql_endpoint)

        if is_list_item:
            query = Template(
                """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                SELECT (COUNT(DISTINCT(?value)) as ?count)
                WHERE {
                    <{{ uri }}> <{{ predicate }}> ?o .
                    ?o rdf:rest* ?rest .
                    ?rest rdf:first ?value
                }
            """
            ).render(uri=uri, predicate=predicate)
        else:
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


def get_predicate_values_query(
    uri: str,
    predicate: str,
    sparql_endpoint: str,
    limit: int,
    page: int,
    profile: str = "",
) -> str:
    is_virtuoso_endpoint = "virtuoso.tern" in sparql_endpoint

    is_list_item = predicate_is_list_item(uri, predicate, sparql_endpoint)

    ProfileClass = get_profile(profile)

    if ProfileClass:
        profile_instance = ProfileClass(uri, [])
        query = profile_instance.get_predicate_values(predicate, limit, page)
    else:
        if is_list_item:
            if is_virtuoso_endpoint:
                # Virtuoso does not work with the BIND clause for predicate, using VALUES instead.
                # BIND 0 causes a "out of index error", so we start list with 1
                query = Template(
                    """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                    SELECT ?p ?o ?listItem ?listItemNumber
                    WHERE {
                        #BIND(<{{ predicate }}> AS ?p)
                        <{{ uri }}> ?p ?_o .
                        VALUES ?p { <{{ predicate }}> }
                        ?_o rdf:rest* ?rest .
                        ?rest rdf:first ?o

                        BIND(EXISTS{?o rdf:rest ?rest} as ?listItem)

                        # This gets set later with the listItemNumber value.
                        BIND(1 AS ?listItemNumber)
                    }
                    GROUP BY ?p ?o ?listItem ?listItemNumber
                    LIMIT {{ limit }}
                    OFFSET {{ offset }}
                """
                ).render(uri=uri, predicate=predicate, limit=limit, offset=(page - 1) * limit)
            else:
                query = Template(
                    """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                    SELECT ?p ?o ?listItem ?listItemNumber
                    WHERE {
                        BIND(<{{ predicate }}> AS ?p)
                        <{{ uri }}> ?p ?_o .
                        ?_o rdf:rest* ?rest .
                        ?rest rdf:first ?o

                        BIND(EXISTS{?o rdf:rest ?rest} as ?listItem)

                        # This gets set later with the listItemNumber value.
                        BIND(0 AS ?listItemNumber)
                    }
                    GROUP BY ?p ?o ?listItem ?listItemNumber
                    LIMIT {{ limit }}
                    OFFSET {{ offset }}
                """
                ).render(uri=uri, predicate=predicate, limit=limit, offset=(page - 1) * limit)
        else:
            if is_virtuoso_endpoint:
                # Virtuoso does not work with the BIND clause for predicate, using VALUES instead.
                # BIND 0 causes a "out of index error", so we start list with 1
                # Also requires to have the ?label in the GROUP BY
                query = Template(
                    """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                    SELECT ?p ?o ?listItem ?listItemNumber (SAMPLE(?_label) AS ?label)
                    WHERE {
                        #BIND(<{{ predicate }}> AS ?p)
                        <{{ uri }}> ?p ?o .
                        VALUES ?p { <{{ predicate }}> }

                        OPTIONAL{
                            ?o skos:prefLabel ?_label .
                        }

                        BIND(EXISTS{?o rdf:rest ?rest} as ?listItem)

                        # This gets set later with the listItemNumber value.
                        BIND(1 AS ?listItemNumber)
                    }
                    GROUP BY ?p ?o ?listItem ?listItemNumber ?label
                    ORDER BY ?label
                    LIMIT {{ limit }}
                    OFFSET {{ offset }}
                """
                ).render(uri=uri, predicate=predicate, limit=limit, offset=(page - 1) * limit)
            else:
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

    return query


def get_predicate_values(
    uri: str, predicate: str, sparql_endpoint: str, profile: str, limit: int, page: int
) -> PredicateValues:
    count = get_predicate_count_index(uri, predicate, sparql_endpoint, profile)
    query = get_predicate_values_query(uri, predicate, sparql_endpoint, limit, page, profile)

    response = sparql.post(query, sparql_endpoint)

    result = response.json()

    # An index of URIs with label values.
    uri_label_index = domain.viewer.resource.json.get_uri_label_index(result, sparql_endpoint)

    # An index of all the URIs linked to and from this resource that are available internally.
    uri_internal_index = domain.viewer.resource.json.get_uri_internal_index(result, sparql_endpoint)

    values = []

    for row in result["results"]["bindings"]:
        item = None

        if row["p"]["value"] == str(RDF.type):
            continue
        else:
            if row["o"]["type"] == "uri":
                object_label = uri_label_index.get(row["o"]["value"]) or row["o"]["value"]
                item = domain.schema.URI(
                    label=object_label,
                    value=row["o"]["value"],
                    internal=uri_internal_index.get(row["o"]["value"], False),
                    list_item=True if row["listItem"]["value"] == "true" else False,
                    list_item_number=row["listItemNumber"]["value"]
                    if row["listItem"]["value"] == "true"
                    else None,
                )
            elif row["o"]["type"] == "literal" or row["o"]["type"] == "typed-literal":
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
                raise ValueError(f"Expected type to be uri or literal but got {row['o']['type']}")

            if item:
                values.append(item)

    predicate_values = PredicateValues(uri=uri, predicate=predicate, objects=values, count=count)
    return predicate_values.json()


def get_predicates(uri: str, sparql_endpoint: str) -> list[URI]:
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
    predicates = get_predicates(uri, sparql_endpoint)
    predicates = list(filter(lambda x: x.value != str(RDF.type), predicates))

    profile_uri = ""
    ProfileClass = None
    for t in types:
        ProfileClass = get_profile(t.value)

        if ProfileClass:
            break

    if ProfileClass:
        profile = ProfileClass(uri, predicates)
        profile.add_and_remove()
        predicates = profile.properties
        profile_uri = profile.uri

    return Resource(
        uri=uri,
        label=label or uri,
        types=types,
        properties=predicates,
        profile=profile_uri,
        properties_require_profile=profile.properties_require_profile if ProfileClass else [],
    ).json()
