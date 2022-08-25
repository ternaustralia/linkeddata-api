from rdflib import RDFS, SKOS, SDO, DCTERMS

from linkeddata_api.vocab_viewer import nrm
from linkeddata_api.vocab_viewer.nrm.namespaces import TERN


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


def method_profile(
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
