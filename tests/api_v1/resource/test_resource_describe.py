import pytest
from pytest_mock import MockerFixture
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
import requests
from rdflib import Graph


@pytest.fixture
def url() -> str:
    return "/api/v1.0/resource"


value = """
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://linked.data.gov.au/def/nrm> a owl:Ontology,
        skos:ConceptScheme ;
    dcterms:hasPart <https://linked.data.gov.au/def/test/dawe-cv/05f83f99-1998-4d11-8837-bb4a68788521>,
        <https://linked.data.gov.au/def/test/dawe-cv/31a9f83d-9c8b-4d68-8dd7-d1b7a9a4197b>,
        <https://linked.data.gov.au/def/test/dawe-cv/dba9fde2-34ba-4a1d-92e0-63846105fc87>,
        <https://linked.data.gov.au/def/test/dawe-cv/e8e10807-baea-4c9b-8d1c-d77ced9df1e9>,
        <https://linked.data.gov.au/def/test/dawe-cv/f46fcbc6-0660-4e12-bcd4-c5642459b630> ;
    dcterms:provenance "The controlled vocabularies are the digital RDF representation of concepts extracted from the DAWE NRM field collection protocols." ;
    skos:definition "The DAWE NRM controlled vocabularies support the data representation of field survey data collected using the NRM collection protocols." ;
    skos:prefLabel "DAWE NRM Controlled Vocabularies" ;
    schema:codeRepository "https://github.com/ternaustralia/dawe-rlp-vocabs"^^xsd:anyURI ;
    schema:contributor <https://w3id.org/tern/resources/3da2112b-74c0-4d9c-bc39-d8dad6e80808> ;
    schema:creator <https://orcid.org/0000-0002-6047-9864>,
        <https://orcid.org/0000-0002-8481-9069>,
        <https://orcid.org/0000-0002-9143-5514>,
        <https://w3id.org/tern/resources/cbd72114-5fa0-410a-b6c1-73a3fd8f111e> ;
    schema:dateCreated "2022-05-19"^^xsd:date ;
    schema:dateIssued "2022-05-19"^^xsd:date ;
    schema:dateModified "2022-05-19"^^xsd:date ;
    schema:license "https://creativecommons.org/licenses/by/4.0/"^^xsd:anyURI ;
    schema:publisher <https://ror.org/030c92375> ;
    schema:url "https://github.com/ternaustralia/dawe-rlp-vocabs/tree/master/vocab_files/index.ttl" .

<https://linked.data.gov.au/def/test/dawe-cv/0033bb3d-fd5a-51eb-ba4b-8c249430aa6d> rdfs:isDefinedBy <https://linked.data.gov.au/def/nrm> .
"""


@pytest.mark.parametrize(
    "mocked_status_code, response_status_code, accept_format, expected_format, uri, repository_id, include_incoming_relationships, content, expected_triples_count",
    [
        # Expected usage
        (
            200,
            200,
            "text/turtle",
            "text/turtle",
            "https://linked.data.gov.au/def/nrm",
            "dawe_vocabs_core",
            "false",
            value,
            22,
        ),
        # URI resource does not exist
        (
            200,
            404,
            "text/turtle",
            "text/html",
            "https://linked.data.gov.au/def/nrm/not-exist",
            "dawe_vocabs_core",
            "false",
            "",
            22,
        ),
        # RDF4J repository does not exist
        (
            415,
            502,
            "text/turtle",
            "text/html",
            "https://linked.data.gov.au/def/nrm",
            "dawe_vocabs_core-not-exist",
            "false",
            "",
            22,
        ),
        # Include incoming relationships
        (
            200,
            200,
            "text/turtle",
            "text/turtle",
            "https://linked.data.gov.au/def/nrm",
            "dawe_vocabs_core",
            "true",
            value,
            23,
        ),
        # No accepted format, default to text/turtle
        (
            200,
            200,
            "",
            "text/turtle",
            "https://linked.data.gov.au/def/nrm",
            "dawe_vocabs_core",
            "false",
            value,
            22,
        ),
    ],
)
def test_describe(
    client: FlaskClient,
    url: str,
    mocker: MockerFixture,
    mocked_status_code: int,
    response_status_code: int,
    accept_format: str,
    expected_format: str,
    uri: str,
    repository_id: str,
    include_incoming_relationships,
    content: str,
    expected_triples_count: int,
):
    mocked_response = requests.Response()
    mocked_response.status_code = mocked_status_code
    mocked_response._content = content.encode("utf-8")

    mocker.patch("requests.get", return_value=mocked_response)

    response: TestResponse = client.get(
        url,
        query_string={
            "repository_id": repository_id,
            "uri": uri,
            "include_incoming_relationships": include_incoming_relationships,
        },
        headers={"accept": accept_format},
    )
    assert response.status_code == response_status_code
    assert expected_format in response.headers.get("content-type")

    if response.status_code == 200:
        graph = Graph()
        graph.parse(data=response.text, format=expected_format)
        assert len(graph) == expected_triples_count
