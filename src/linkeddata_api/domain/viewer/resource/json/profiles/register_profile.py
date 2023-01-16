from linkeddata_api.domain.viewer.resource.json.profiles import (
    register_profile,
)
from linkeddata_api.domain.viewer.resource.json.profiles.custom_profiles import (
    MethodCollectionProfile,
    MethodProfile,
)


register_profile(
    "https://w3id.org/tern/ontologies/tern/MethodCollection",
    MethodCollectionProfile,
)
register_profile(
    "https://w3id.org/tern/ontologies/tern/Method",
    MethodProfile,
)
