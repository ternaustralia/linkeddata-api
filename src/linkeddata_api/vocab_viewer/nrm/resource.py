from rdflib import RDF

from linkeddata_api.vocab_viewer import nrm


def get(
    uri: str,
    profile: str = None,
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
        label = nrm.label.get(uri, sparql_endpoint)
        types = []
        properties = []
        # TODO: Do a lookup with sparql to check if URI is internal.
        for row in result["results"]["bindings"]:
            if row["p"]["value"] == str(RDF.type):
                types.append(
                    nrm.schema.URI(
                        label="rdf:type",
                        value=row["o"]["value"],
                        internal=False,  # TODO
                    )
                )
            else:
                predicate_label = nrm.curie.get(row["p"]["value"])
                predicate = nrm.schema.URI(
                    label=predicate_label,
                    value=row["p"]["value"],
                    internal=False,  # TODO
                )
                if row["o"]["type"] == "uri":
                    curie = nrm.label.get(
                        row["o"]["value"], sparql_endpoint
                    ) or nrm.curie.get(row["o"]["value"])
                    item = nrm.schema.URI(
                        label=curie,
                        value=row["o"]["value"],
                        internal=False,  # TODO
                    )
                elif row["o"]["type"] == "literal":
                    item = nrm.schema.Literal(value=row["o"]["value"])
                else:
                    raise ValueError(
                        f"Expected type to be uri or literal but got {row['o']['value']}"
                    )  # TODO
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
    except Exception as err:
        if result == {"head": {"vars": ["p", "o"]}, "results": {"bindings": []}}:
            raise nrm.exceptions.SPARQLNotFoundError(
                f"Resource with URI {uri} not found."
            )
        raise nrm.exceptions.SPARQLResultJSONError(
            f"Unexpected SPARQL result.\n{result}\n{err}"
        ) from err
