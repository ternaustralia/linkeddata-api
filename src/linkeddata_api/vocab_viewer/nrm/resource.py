from rdflib import RDF, RDFS, SKOS, SDO, DCTERMS

from linkeddata_api.vocab_viewer import nrm
from linkeddata_api.vocab_viewer.nrm.namespaces import TERN


def _exists_uri(target_uri: str, uris: list[nrm.schema.URI]) -> bool:
    for uri in uris:
        if uri.value == target_uri:
            return True
    return False


def _add_and_remove_property(
    predicate_uri: str,
    old_list: list[nrm.schema.PredicateObjects],
    new_list: list[nrm.schema.PredicateObjects],
) -> None:
    """Add and remove the PredicateObjects object if matched by predicate_uri in
    the referenced lists, 'old_list' and 'new_list'

    Returns a copy of the PredicateObjects object.
    """
    predicate_object = None
    for property_ in old_list:
        if property_.predicate.value == predicate_uri:
            new_list.append(property_)
            predicate_object = property_
            old_list.remove(property_)
    return predicate_object


def _method_profile(
    properties: list[nrm.schema.PredicateObjects],
) -> list[nrm.schema.PredicateObjects]:
    new_properties = []

    _add_and_remove_property(str(RDFS.isDefinedBy), properties, new_properties)

    # Omit skos:prefLabel
    _add_and_remove_property(str(SKOS.prefLabel), properties, new_properties)
    new_properties.pop()

    _add_and_remove_property(str(TERN), properties, new_properties)
    _add_and_remove_property(str(SDO.url), properties, new_properties)
    _add_and_remove_property(str(SKOS.memberList), properties, new_properties)
    _add_and_remove_property(str(TERN.scope), properties, new_properties)
    _add_and_remove_property(str(SKOS.definition), properties, new_properties)
    _add_and_remove_property(str(TERN.purpose), properties, new_properties)
    # TODO: Change to different property due to issue with RVA
    _add_and_remove_property(str(DCTERMS.description), properties, new_properties)
    _add_and_remove_property(str(TERN.equipment), properties, new_properties)
    _add_and_remove_property(str(TERN.instructions), properties, new_properties)
    _add_and_remove_property(str(SKOS.note), properties, new_properties)
    _add_and_remove_property(str(DCTERMS.source), properties, new_properties)
    _add_and_remove_property(str(TERN.appendix), properties, new_properties)

    return new_properties + properties


def _get_rdf_list_item_uris(uri: str, rows: list, sparql_endpoint: str) -> list[str]:
    new_uris = []
    for row in rows:
        if row["o"]["type"] == "bnode" and row["listItem"]["value"] == "true":
            # TODO: error handling - move empty result exception to nrm.sparql.post
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
            result = nrm.sparql.post(
                query,
                sparql_endpoint,
            )

            for result_row in result["results"]["bindings"]:
                new_uris.append(result_row)

    return new_uris


def _get_rdf_list_item_as_uri_objects(
    uri: str,
    predicate_uri: str,
    sparql_endpoint: str,
    uri_label_index: dict,
    uri_internal_index: dict,
) -> list[nrm.schema.URI]:
    uri_objects = []
    # TODO: error handling - move empty result exception to nrm.sparql.post
    result = nrm.sparql.post(
        f"""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?item 
        where {{
            BIND(<{predicate_uri}> AS ?p)
            <{uri}> ?p ?list .
            ?list rdf:rest* ?rest .
            ?rest rdf:first ?item .
        }}
    """,
        sparql_endpoint,
    )
    return result["results"]["bindings"]
    # for row in result["results"]["bindings"]:
    #     uri_objects.append(result["item"]["value"])

    # return uri_objects


def get(
    uri: str,
    profile: str = None,  # TODO: Add presentation handling for different kinds of data
    sparql_endpoint: str = "https://graphdb.tern.org.au/repositories/dawe_vocabs_core",
) -> nrm.schema.Resource:
    query = f"""
        SELECT ?p ?o ?listItem ?listItemNumber
        WHERE {{
            <{uri}> ?p ?o .
            BIND(EXISTS{{?o rdf:rest ?rest}} as ?listItem)
            
            # This gets set later with the listItemNumber value.
            BIND(0 AS ?listItemNumber)
        }}
    """

    result = nrm.sparql.post(query, sparql_endpoint)

    try:
        uri = uri
        types = []
        properties = []

        uri_values = filter(
            lambda x: x["o"]["type"] == "uri", result["results"]["bindings"]
        )

        uri_values = [value["o"]["value"] for value in uri_values]
        uri_values.append(uri)

        # Replace value of blank node list head with items.
        list_items = _get_rdf_list_item_uris(
            uri, result["results"]["bindings"], sparql_endpoint
        )

        for row in list_items:
            uri_values.append(row["o"]["value"])

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

        uri_label_index = nrm.label.get_from_list(uri_values, sparql_endpoint)

        label = nrm.label.get(uri, sparql_endpoint) or uri

        uri_internal_index = nrm.internal_resource.get_from_list(uri_values)

        if not uri_internal_index.get(uri):
            raise nrm.exceptions.SPARQLNotFoundError(
                f"Resource with URI {uri} not found."
            )

        for row in result["results"]["bindings"]:
            if row["p"]["value"] == str(RDF.type):
                type_label = uri_label_index.get(row["o"]["value"]) or nrm.curie.get(
                    row["o"]["value"]
                )
                types.append(
                    nrm.schema.URI(
                        label=type_label,
                        value=row["o"]["value"],
                        internal=uri_internal_index.get(row["o"]["value"], False),
                    )
                )
            else:
                predicate_label = nrm.curie.get(row["p"]["value"])
                predicate = nrm.schema.URI(
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
                    ) or nrm.curie.get(row["o"]["value"])
                    item = nrm.schema.URI(
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
                        datatype = nrm.schema.URI(
                            label=datatype,
                            value=datatype,
                            internal=uri_internal_index.get(datatype, False),
                            list_item=True
                            if row["listItem"]["value"] == "true"
                            else False,
                            list_item_number=row["listItemNumber"]["value"]
                            if row["listItem"]["value"] == "true"
                            else None,
                        )
                    else:
                        datatype = None

                    item = nrm.schema.Literal(
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
                        nrm.schema.PredicateObjects(predicate=predicate, objects=[item])
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

        profile = ""
        if _exists_uri("https://w3id.org/tern/ontologies/tern/MethodCollection", types):
            profile = "https://w3id.org/tern/ontologies/tern/MethodCollection"
            properties = _method_profile(properties)
        elif _exists_uri("https://w3id.org/tern/ontologies/tern/Method", types):
            profile = "https://w3id.org/tern/ontologies/tern/Method"

        return nrm.schema.Resource(
            uri=uri, profile=profile, label=label, types=types, properties=properties
        )
    except nrm.exceptions.SPARQLNotFoundError as err:
        raise err
    except Exception as err:
        raise nrm.exceptions.SPARQLResultJSONError(
            f"Unexpected SPARQL result.\n{result}\n{err}"
        ) from err


def sort_property_objects(x):
    if x.list_item:
        return x.list_item_number
    else:
        if x.type == "uri":
            return x.label
        else:
            return x.value
