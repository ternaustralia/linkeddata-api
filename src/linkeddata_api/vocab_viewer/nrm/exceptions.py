class RequestError(Exception):
    """Request Exception"""

    def __init__(self, description: str) -> None:
        super().__init__(description)
        self.description = description


class SPARQLResultJSONError(Exception):
    """SPARQL Result JSON Error"""

    def __init__(self, description: str) -> None:
        super().__init__(description)
        self.description = description
