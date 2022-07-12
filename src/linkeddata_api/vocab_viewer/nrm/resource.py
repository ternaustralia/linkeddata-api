from rdflib import RDF

from linkeddata_api.vocab_viewer import nrm


def get(
    uri: str,
    profile: str = None,  # TODO: Add presentation handling for different kinds of data
    sparql_endpoint: str = "https://graphdb.tern.org.au/repositories/dawe_vocabs_core",
) -> nrm.schema.Resource:
    query = f"""
        SELECT *
        WHERE {{
            <{uri}> ?p ?o .
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
                )
                if row["o"]["type"] == "uri":
                    object_label = uri_label_index.get(
                        row["o"]["value"]
                    ) or nrm.curie.get(row["o"]["value"])
                    item = nrm.schema.URI(
                        label=object_label,
                        value=row["o"]["value"],
                        internal=uri_internal_index.get(row["o"]["value"], False),
                    )
                elif row["o"]["type"] == "literal":
                    datatype = row["o"].get("datatype", "")
                    if datatype:
                        datatype = nrm.schema.URI(
                            label=datatype,
                            value=datatype,
                            internal=uri_internal_index.get(datatype, False),
                        )
                    else:
                        datatype = None

                    item = nrm.schema.Literal(
                        value=row["o"]["value"],
                        datatype=datatype,
                        language=row["o"].get("xml:lang", ""),
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

        return nrm.schema.Resource(
            uri=uri, label=label, types=types, properties=properties
        )
    except nrm.exceptions.SPARQLNotFoundError as err:
        raise err
    except Exception as err:
        raise nrm.exceptions.SPARQLResultJSONError(
            f"Unexpected SPARQL result.\n{result}\n{err}"
        ) from err
