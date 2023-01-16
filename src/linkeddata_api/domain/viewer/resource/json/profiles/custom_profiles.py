from rdflib import RDFS, SKOS, SDO, DCTERMS

from linkeddata_api.domain.namespaces import TERN
from linkeddata_api.domain.viewer.resource.json.profiles import Profile
from linkeddata_api.domain.schema import PredicateObjects, URI, Literal


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

    def add_and_remove(self):
        super().add_and_remove()
        print("printing from method profile")
        print("resource uri", self.resource_uri)
        # Fetch observable properties
        # Fetch feature types
        # Fetch categorical values

        predicate = URI(label="hello", value="https://example.com", internal=False)
        objects = [
            URI(label="world", value="https://example.com/world", internal=False),
            Literal(value="Tada, this is a literal!"),
        ]

        a = PredicateObjects(predicate=predicate, objects=objects)

        self.properties.append(a)
