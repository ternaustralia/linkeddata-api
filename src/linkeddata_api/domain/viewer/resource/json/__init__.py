from rdflib import RDF

from linkeddata_api import data, domain
from linkeddata_api.domain.viewer.resource.json.exists_uri import exists_uri
from linkeddata_api.domain.viewer.resource.json.profiles import method_profile
from linkeddata_api.domain.viewer.resource.json.sort_property_objects import (
    sort_property_objects,
)


def _get_uris_from_rdf_list(uri: str, rows: list, sparql_endpoint: str) -> list[str]:
    new_uris = []
    for row in rows:
        if row["o"]["type"] == "bnode" and row["listItem"]["value"] == "true":
            # TODO: error handling - move empty result exception to nrm.sparql.post/nrm.sparql.get
            query = f"""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                SELECT DISTINCT ?p ?o
                where {{
                    BIND(<{row["p"]["value"]}> AS ?p)
                    <{uri}> ?p ?list .
                    ?list rdf:rest* ?rest .
                    ?rest rdf:first ?o .
                }}
            """
            result = data.sparql.post(
                query,
                sparql_endpoint,
            )

            for result_row in result["results"]["bindings"]:
                new_uris.append(result_row)

    return new_uris


def _get_uri_values_and_list_items(
    result: dict, uri: str, sparql_endpoint: str
) -> tuple[list[str], list[str]]:
    uri_values = filter(
        lambda x: x["o"]["type"] == "uri", result["results"]["bindings"]
    )

    uri_values = [value["o"]["value"] for value in uri_values]
    uri_values.append(uri)

    # Replace value of blank node list head with items.
    list_items = _get_uris_from_rdf_list(
        uri, result["results"]["bindings"], sparql_endpoint
    )

    for row in list_items:
        uri_values.append(row["o"]["value"])

    return uri_values, list_items


def _add_rows_for_rdf_list_items(result: dict, uri: str, sparql_endpoint: str) -> dict:
    """Add rdf:List items as new rows to the SPARQL result object

    :param result: The SPARQL result dict object
    :param uri: URI of the resource
    :param sparql_endpoint: SPARQL endpoint to fetch the list items from
    :return: An updated SPARQL result dict object
    """
    _, list_items = _get_uri_values_and_list_items(result, uri, sparql_endpoint)

    # Add additional rows to the `result` representing the RDF List items.
    for i, list_item in enumerate(list_items):
        list_item.update(
            {
                "listItem": {
                    "datatype": "http://www.w3.org/2001/XMLSchema#boolean",
                    "type": "literal",
                    "value": "true",
                },
                "listItemNumber": {
                    "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                    "type": "literal",
                    "value": str(i),
                },
            }
        )
        result["results"]["bindings"].append(list_item)

    return result


def _get_uri_label_index(
    result: dict, uri: str, sparql_endpoint: str
) -> dict[str, str]:
    uri_values, _ = _get_uri_values_and_list_items(result, uri, sparql_endpoint)
    uri_label_index = domain.label.get_from_list(uri_values, sparql_endpoint)
    return uri_label_index


def _get_uri_internal_index(
    result: dict, uri: str, sparql_endpoint: str
) -> dict[str, str]:
    uri_values, _ = _get_uri_values_and_list_items(result, uri, sparql_endpoint)
    uri_internal_index = domain.internal_resource.get_from_list(
        uri_values, sparql_endpoint
    )
    return uri_internal_index


def get(uri: str, sparql_endpoint: str) -> domain.schema.Resource:
    query = f"""
        SELECT ?p ?o ?listItem ?listItemNumber
        WHERE {{
            <{uri}> ?p ?o .
            BIND(EXISTS{{?o rdf:rest ?rest}} as ?listItem)
            
            # This gets set later with the listItemNumber value.
            BIND(0 AS ?listItemNumber)
        }}
    """

    result = data.sparql.post(query, sparql_endpoint).json()

    try:
        result = _add_rows_for_rdf_list_items(result, uri, sparql_endpoint)
        label = domain.label.get(uri, sparql_endpoint) or uri
        types, properties = _get_types_and_properties(result, uri, sparql_endpoint)

        profile = ""
        if exists_uri("https://w3id.org/tern/ontologies/tern/MethodCollection", types):
            profile = "https://w3id.org/tern/ontologies/tern/MethodCollection"
            properties = method_profile(properties)
        elif exists_uri("https://w3id.org/tern/ontologies/tern/Method", types):
            profile = "https://w3id.org/tern/ontologies/tern/Method"
            properties = method_profile(properties)

        incoming_properties = _get_incoming_properties(uri, sparql_endpoint)

        return domain.schema.Resource(
            uri=uri,
            profile=profile,
            label=label,
            types=types,
            properties=properties,
            # incoming_properties=incoming_properties,
            incoming_properties=[],  # TODO:
        )
    except data.exceptions.SPARQLNotFoundError as err:
        raise err
    except Exception as err:
        raise data.exceptions.SPARQLResultJSONError(
            f"Unexpected SPARQL result.\n{result}\n{err}"
        ) from err


def _get_incoming_properties(uri: str, sparql_endpoint: str):
    query = f"""
        SELECT ?p ?o ?listItem ?listItemNumber
        WHERE {{
            ?o ?p <{uri}> .

            # This is not required for `incoming_properties`
            # but we need to set the values for compatibility with `properties`.
            BIND(EXISTS{{?o rdf:rest ?rest}} as ?listItem)
            BIND(0 AS ?listItemNumber)
        }}
    """

    result = data.sparql.post(
        query,
        sparql_endpoint,
    ).json()

    uri_label_index = _get_uri_label_index(result, uri, sparql_endpoint)
    uri_internal_index = _get_uri_internal_index(result, uri, sparql_endpoint)

    incoming_properties = []

    for row in result["results"]["bindings"]:
        subject_label = uri_label_index.get(row["o"]["value"]) or domain.curie.get(
            row["o"]["value"]
        )
        item = domain.schema.URI(
            label=subject_label,
            value=row["o"]["value"],
            internal=uri_internal_index.get(row["o"]["value"], False),
            list_item=True if row["listItem"]["value"] == "true" else False,
            list_item_number=row["listItemNumber"]["value"]
            if row["listItem"]["value"] == "true"
            else None,
        )
        predicate_label = domain.curie.get(row["p"]["value"])
        predicate = domain.schema.URI(
            label=predicate_label,
            value=row["p"]["value"],
            internal=uri_internal_index.get(row["p"]["value"], False),
            list_item=True if row["listItem"]["value"] == "true" else False,
            list_item_number=int(row["listItemNumber"]["value"])
            if row["listItem"]["value"] == "true"
            else None,
        )

        found = False
        for p in incoming_properties:
            if p.predicate.value == predicate.value:
                found = True
                p.subjects.append(item)

        if not found:
            incoming_properties.append(
                domain.schema.SubjectPredicates(predicate=predicate, subjects=[item])
            )

    return incoming_properties


def _get_types_and_properties(
    result: dict, uri: str, sparql_endpoint: str
) -> tuple[list[domain.schema.URI], list[domain.schema.PredicateObjects]]:

    types: list[domain.schema.URI] = []
    properties: list[domain.schema.PredicateObjects] = []

    # An index of URIs with label values.
    uri_label_index = _get_uri_label_index(result, uri, sparql_endpoint)

    # An index of all the URIs linked to and from this resource that are available internally.
    uri_internal_index = _get_uri_internal_index(result, uri, sparql_endpoint)

    if not uri_internal_index.get(uri):
        raise data.exceptions.SPARQLNotFoundError(f"Resource with URI {uri} not found.")

    for row in result["results"]["bindings"]:
        if row["p"]["value"] == str(RDF.type):
            type_label = uri_label_index.get(row["o"]["value"]) or domain.curie.get(
                row["o"]["value"]
            )
            types.append(
                domain.schema.URI(
                    label=type_label,
                    value=row["o"]["value"],
                    internal=uri_internal_index.get(row["o"]["value"], False),
                )
            )
        else:
            predicate_label = domain.curie.get(row["p"]["value"])
            predicate = domain.schema.URI(
                label=predicate_label,
                value=row["p"]["value"],
                internal=uri_internal_index.get(row["p"]["value"], False),
                list_item=True if row["listItem"]["value"] == "true" else False,
                list_item_number=int(row["listItemNumber"]["value"])
                if row["listItem"]["value"] == "true"
                else None,
            )
            if row["o"]["type"] == "uri":
                object_label = uri_label_index.get(
                    row["o"]["value"]
                ) or domain.curie.get(row["o"]["value"])
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

            found = False
            for p in properties:
                if p.predicate.value == predicate.value:
                    found = True
                    p.objects.append(item)

            if not found:
                properties.append(
                    domain.schema.PredicateObjects(predicate=predicate, objects=[item])
                )

    # Duplicates may occur due to processing RDF lists.
    # Remove duplicates, if any.
    for property_ in properties:
        if property_.predicate.list_item:
            for obj in property_.objects:
                if not obj.list_item:
                    property_.objects.remove(obj)

    # Sort all property objects by label.
    properties.sort(key=lambda x: x.predicate.label)
    for property_ in properties:
        property_.objects.sort(key=sort_property_objects)

    return types, properties
