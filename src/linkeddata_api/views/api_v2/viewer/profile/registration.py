from .base_profile import register_profile
from .custom_profiles import MethodCollectionProfile, MethodProfile


register_profile(
    "https://w3id.org/tern/ontologies/tern/MethodCollection",
    MethodCollectionProfile,
)
register_profile(
    "https://w3id.org/tern/ontologies/tern/Method",
    MethodProfile,
)
