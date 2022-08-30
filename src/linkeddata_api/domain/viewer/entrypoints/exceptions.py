from linkeddata_api.data.exceptions import RequestError, SPARQLResultJSONError


class ViewerIDNotFoundError(Exception):
    """This is raised when an unrecognised viewer ID is provided"""
