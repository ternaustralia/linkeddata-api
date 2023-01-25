from typing import Union
from abc import ABCMeta, abstractmethod

from ..schema import URI


profiles = {}


class Profile(metaclass=ABCMeta):
    resource_uri: str
    properties: list[URI]
    properties_require_profile: list[str] = []

    def __init__(self, resource_uri: str, properties: list[URI]) -> None:
        self.resource_uri = resource_uri
        self.properties = properties

    @staticmethod
    def _add_and_remove_property(
        predicate_uri: str,
        old_list: list[URI],
        new_list: list[URI],
    ) -> Union[URI, None]:
        """Add and remove the PredicateObjects object if matched by predicate_uri in
        the referenced lists, 'old_list' and 'new_list'

        Returns a copy of the PredicateObjects object, if found, else None.

        Use linkeddata_api.domain.curie.get() to get the label of predicates.
        Use linkeddata_api.domain.label.get_from_list() to get a dict of labels for the values.
        """
        for uri in old_list:
            if uri.value == predicate_uri:
                new_list.append(uri)

                old_list.remove(uri)
                return uri

    @property
    def uri(self) -> str:
        """Get the URI of the RDF class this profile targets"""
        return self._uri()

    @abstractmethod
    def _uri(self) -> str:
        ...

    @abstractmethod
    def add_and_remove(self):
        ...


def register_profile(uri: str, profile_class: type[Profile]) -> None:
    profiles.update({uri: profile_class})


def get_profile(uri) -> type[Profile] | None:
    try:
        profile = profiles[uri]
        return profile
    except KeyError:
        pass


# Register the profiles with an import statement
from . import registration
