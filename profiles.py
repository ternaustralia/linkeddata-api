class ProfileBase:
    def __init__(self) -> None:
        pass

    def add_and_remove(self):
        pass


class MethodCollectionProfile(ProfileBase):
    profile = "https://w3id.org/tern/ontologies/tern/MethodCollection"

    def __init__(self) -> None:
        super().__init__()

    def add_and_remove(self):
        super().add_and_remove()
        print("printing from method collection")


class MethodProfile(MethodCollectionProfile):
    profile = "https://w3id.org/tern/ontologies/tern/MethodCollection"

    def __init__(self) -> None:
        super().__init__()

    def add_and_remove(self):
        super().add_and_remove()
        print("printing from method profile")


profiles = {}


def register_profile(uri: str, profile_class: type[ProfileBase]) -> None:
    profiles.update({uri: profile_class})
    # profiles[uri]: profile_class


def get_profile(uri) -> type[ProfileBase] | None:
    try:
        profile = profiles[uri]
        return profile
    except KeyError as err:
        # raise ProfileNotFoundError(f"No profiles found for URI {uri}") from err
        pass


class ProfileNotFoundError(Exception):
    pass


def main():
    register_profile(
        "https://w3id.org/tern/ontologies/tern/MethodCollection",
        MethodCollectionProfile,
    )
    register_profile(
        "https://w3id.org/tern/ontologies/tern/Method",
        MethodProfile,
    )
    print(profiles)

    types = ["https://w3id.org/tern/ontologies/tern/Method"]

    profile = None
    for t in types:
        profile = get_profile(t)
        if profile:
            break

    if profile:
        p = profile()
        p.add_and_remove()
        print(p.profile)

    # found = False
    # for uri, profile_class in profiles.items():
    #     if uri in types:
    #         profile_class()
    #         found = True
    #         break

    #     if found:
    #         break

    # if found:
    #     print("Found: profile uri: ", profile_class.profile)


if __name__ == "__main__":
    main()
