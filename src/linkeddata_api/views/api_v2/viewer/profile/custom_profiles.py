from jinja2 import Template
from rdflib import RDFS, SKOS, SDO, DCTERMS

from linkeddata_api.data import sparql
from linkeddata_api.domain.namespaces import TERN

from .base_profile import Profile
from ..schema import PredicateValues, URI


class MethodCollectionProfile(Profile):
    def _uri(self) -> str:
        return "https://w3id.org/tern/ontologies/tern/MethodCollection"

    def add_and_remove(self):
        super().add_and_remove()

        properties = self.properties
        new_properties = []

        self._add_and_remove_property(str(RDFS.isDefinedBy), properties, new_properties)

        self._add_and_remove_property(str(SKOS.prefLabel), properties, new_properties)
        # Pop to omit skos:prefLabel property
        new_properties.pop()

        self._add_and_remove_property(str(TERN), properties, new_properties)
        self._add_and_remove_property(str(SDO.url), properties, new_properties)
        self._add_and_remove_property(str(SKOS.memberList), properties, new_properties)
        self._add_and_remove_property(str(TERN.scope), properties, new_properties)
        self._add_and_remove_property(str(SKOS.definition), properties, new_properties)
        self._add_and_remove_property(str(TERN.purpose), properties, new_properties)
        self._add_and_remove_property(
            str(DCTERMS.description), properties, new_properties
        )
        self._add_and_remove_property(str(TERN.equipment), properties, new_properties)
        self._add_and_remove_property(
            str(TERN.instructions), properties, new_properties
        )
        self._add_and_remove_property(str(SKOS.note), properties, new_properties)
        self._add_and_remove_property(str(DCTERMS.source), properties, new_properties)
        self._add_and_remove_property(str(TERN.appendix), properties, new_properties)

        self.properties = new_properties + properties


class MethodProfile(MethodCollectionProfile):
    properties_require_profile = [
        "https://w3id.org/tern/ontologies/tern/hasObservableProperty",
        "https://w3id.org/tern/ontologies/tern/hasFeatureType",
        "https://w3id.org/tern/ontologies/tern/hasCategoricalValuesCollection",
    ]

    def _uri(self) -> str:
        return "https://w3id.org/tern/ontologies/tern/Method"

    def get_additional_values(
        self,
        metadata_predicate: str,
        predicate: str,
        limit: int,
        page: int,
    ):
        query = Template(
            """
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX tern: <https://w3id.org/tern/ontologies/tern/>
            select ?p ?o ?listItem ?listItemNumber (SAMPLE(?_label) AS ?label)
            where {
                ?_observable_property_meta <urn:property:protocolModule> <{{ uri }}> ;
                    <{{ metadata_predicate }}> ?_object_value .
                BIND(<{{ predicate }}> AS ?p)
                BIND(?_object_value AS ?o)
                BIND(false AS ?listItem)

                OPTIONAL{
                    ?o skos:prefLabel ?_label .
                }
                
                # This gets set later with the listItemNumber value.
                BIND(0 AS ?listItemNumber)
            }
            GROUP BY ?p ?o ?listItem ?listItemNumber
            ORDER BY ?label
            LIMIT {{ limit }}
            OFFSET {{ offset }}
        """
        ).render(
            uri=self.resource_uri,
            metadata_predicate=metadata_predicate,
            predicate=predicate,
            limit=limit,
            offset=(page - 1) * limit,
        )

        return query

    def _get_predicate_values_count(
        self, metadata_predicate: str, sparql_endpoint: str
    ) -> int:
        query = Template(
            """
            SELECT (COUNT(DISTINCT(?value)) as ?count)
            WHERE {
                ?_observable_property_meta <urn:property:protocolModule> <{{ uri }}> ;
                    <{{ metadata_predicate }}> ?value .
            }
            """
        ).render(uri=self.resource_uri, metadata_predicate=metadata_predicate)

        response = sparql.post(query, sparql_endpoint)

        count = int(response.json()["results"]["bindings"][0]["count"]["value"])

        return count

    def get_predicate_values_count(self, predicate: str, sparql_endpoint: str) -> int:
        if predicate == "https://w3id.org/tern/ontologies/tern/hasObservableProperty":
            return self._get_predicate_values_count(
                "urn:property:observableProperty", sparql_endpoint
            )
        if predicate == "https://w3id.org/tern/ontologies/tern/hasFeatureType":
            return self._get_predicate_values_count(
                "urn:property:featureType", sparql_endpoint
            )
        if (
            predicate
            == "https://w3id.org/tern/ontologies/tern/hasCategoricalValuesCollection"
        ):
            return self._get_predicate_values_count(
                "urn:property:categoricalValuesCollection", sparql_endpoint
            )

    def get_predicate_values(
        self, predicate: str, limit: int, page: int
    ) -> list[PredicateValues]:

        if predicate == "https://w3id.org/tern/ontologies/tern/hasObservableProperty":
            return self.get_additional_values(
                "urn:property:observableProperty",
                "https://w3id.org/tern/ontologies/tern/hasObservableProperty",
                limit,
                page,
            )
        if predicate == "https://w3id.org/tern/ontologies/tern/hasFeatureType":
            return self.get_additional_values(
                "urn:property:featureType",
                "https://w3id.org/tern/ontologies/tern/hasFeatureType",
                limit,
                page,
            )
        if (
            predicate
            == "https://w3id.org/tern/ontologies/tern/hasCategoricalValuesCollection"
        ):
            return self.get_additional_values(
                "urn:property:categoricalValuesCollection",
                "https://w3id.org/tern/ontologies/tern/hasCategoricalValuesCollection",
                limit,
                page,
            )

    def add_and_remove(self):
        super().add_and_remove()

        self.properties += [
            URI(
                label="tern:hasObservableProperty",
                value="https://w3id.org/tern/ontologies/tern/hasObservableProperty",
                internal=False,
            ),
            URI(
                label="tern:hasFeatureType",
                value="https://w3id.org/tern/ontologies/tern/hasFeatureType",
                internal=False,
            ),
            URI(
                label="tern:hasCategoricalValuesCollection",
                value="https://w3id.org/tern/ontologies/tern/hasCategoricalValuesCollection",
                internal=False,
            ),
        ]
