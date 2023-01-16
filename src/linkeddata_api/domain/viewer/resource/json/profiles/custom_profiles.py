from jinja2 import Template
from rdflib import RDFS, SKOS, SDO, DCTERMS

from linkeddata_api.data import sparql
from linkeddata_api.domain.namespaces import TERN
from linkeddata_api.domain.viewer.resource.json.profiles import Profile
from linkeddata_api.domain.schema import PredicateObjects


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
    def _uri(self) -> str:
        return "https://w3id.org/tern/ontologies/tern/Method"

    @staticmethod
    def _process_sparql_values(results: dict) -> list[PredicateObjects]:
        from linkeddata_api.domain.viewer.resource.json import _get_types_and_properties

        _, properties = _get_types_and_properties(
            results,
            "https://graphdb.tern.org.au/repositories/dawe_vocabs_core",
        )

        return properties

    def get_additional_values(self, metadata_predicate: str, predicate: str):
        query = Template(
            """
            PREFIX tern: <https://w3id.org/tern/ontologies/tern/>
            select *
            where {
                ?_observable_property_meta <urn:property:protocolModule> <{{ uri }}> ;
                    <{{ metadata_predicate }}> ?_object_value .
                BIND(<{{ predicate }}> AS ?p)
                BIND(?_object_value AS ?o)
                BIND(false AS ?listItem)
                
                # This gets set later with the listItemNumber value.
                BIND(0 AS ?listItemNumber)
            }
        """
        ).render(
            uri=self.resource_uri,
            metadata_predicate=metadata_predicate,
            predicate=predicate,
        )

        response = sparql.post(
            query=query,
            sparql_endpoint="https://graphdb.tern.org.au/repositories/dawe_vocabs_core",
        )

        properties = self._process_sparql_values(response.json())

        self.properties += properties

    def add_and_remove(self):
        super().add_and_remove()

        self.get_additional_values(
            "urn:property:observableProperty",
            "https://w3id.org/tern/ontologies/tern/hasObservableProperty",
        )

        self.get_additional_values(
            "urn:property:featureType",
            "https://w3id.org/tern/ontologies/tern/hasFeatureType",
        )

        self.get_additional_values(
            "urn:property:categoricalValuesCollection",
            "https://w3id.org/tern/ontologies/tern/hasCategoricalValuesCollection",
        )
