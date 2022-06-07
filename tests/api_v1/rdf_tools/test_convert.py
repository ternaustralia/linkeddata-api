import json

import pytest

from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from rdflib import Graph
from rdflib.compare import isomorphic


@pytest.fixture
def url() -> str:
    return "/api/v1.0/rdf_tools/convert"


@pytest.mark.parametrize(
    "source_data, source_format, target_data, target_format",
    [
        (
            """{
  "@context": {
    "featureType": {
      "@id": "https://w3id.org/tern/ontologies/tern/featureType",
      "@type": "@id"
    },
    "hasFeatureOfInterest": {
      "@id": "http://www.w3.org/ns/sosa/hasFeatureOfInterest",
      "@type": "@id"
    },
    "observedProperty": {
      "@id": "http://www.w3.org/ns/sosa/observedProperty",
      "@type": "@id"
    },
    "usedProcedure": {
      "@id": "http://www.w3.org/ns/sosa/usedProcedure",
      "@type": "@id"
    },
    "hasResult": {
      "@id": "http://www.w3.org/ns/sosa/hasResult",
      "@type": "@id"
    },
    "value": {
      "@id": "http://www.w3.org/1999/02/22-rdf-syntax-ns#value"
    },
    "vocabulary": {
      "@id": "https://w3id.org/tern/ontologies/tern/vocabulary",
      "@type": "@id"
    },
    "phenomenonTime": {
      "@id": "http://www.w3.org/ns/sosa/phenomenonTime"
    },
    "resultTime": {
      "@id": "http://www.w3.org/ns/sosa/resultTime",
      "@type": "http://www.w3.org/2001/XMLSchema#dateTime"
    },
    "inDataset": {
      "@id": "http://rdfs.org/ns/void#inDataset",
      "@type": "@id"
    },
    "hasSimpleResult": {
      "@id": "http://www.w3.org/ns/sosa/hasSimpleResult"
    },
    "isResultOf": {
      "@id": "http://www.w3.org/ns/sosa/isResultOf",
      "@type": "@id"
    },
    "inXSDDateTimeStamp": {
      "@id": "http://www.w3.org/2006/time#inXSDDateTimeStamp"
    },
    "unit": {
      "@id": "https://w3id.org/tern/ontologies/tern/unit",
      "@type": "@id"
    },
    "hasGeometry": {
      "@id": "http://www.opengis.net/ont/geosparql#hasGeometry",
      "@type": "@id"
    },
    "label": {
      "@id": "http://www.w3.org/2000/01/rdf-schema#label"
    },
    "dimension": {
      "@id": "https://w3id.org/tern/ontologies/tern/dimension"
    },
    "locationDescription": {
      "@id": "https://w3id.org/tern/ontologies/tern/locationDescription"
    },
    "siteDescription": {
      "@id": "https://w3id.org/tern/ontologies/tern/siteDescription"
    },
    "polygon": {
      "@id": "https://w3id.org/tern/ontologies/tern/polygon",
      "@type": "@id"
    },
    "type": {
      "@id": "http://purl.org/dc/terms/type",
      "@type": "@id"
    },
    "asWKT": {
      "@id": "http://www.opengis.net/ont/geosparql#asWKT",
      "@type": "http://www.opengis.net/ont/geosparql#wktLiteral"
    },
    "lat": {
      "@id": "http://www.w3.org/2003/01/geo/wgs84_pos#lat"
    },
    "long": {
      "@id": "http://www.w3.org/2003/01/geo/wgs84_pos#long"
    },
    "pointType": {
      "@id": "https://w3id.org/tern/ontologies/loc/pointType",
      "@type": "@id"
    },
    "title": {
      "@id": "http://purl.org/dc/terms/title",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "issued": {
      "@id": "http://purl.org/dc/terms/issued"
    },
    "description": {
      "@id": "http://purl.org/dc/terms/description",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    }
  },
  "@graph": [
    {
      "@id": "https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd",
      "@type": "https://w3id.org/tern/ontologies/tern/Observation",
      "hasFeatureOfInterest": {
        "@id": "https://example.com/feature-of-interest/66fa9efd-45f1-41d6-bef8-3c7e2e423f3d",
        "@type": "https://w3id.org/tern/ontologies/tern/FeatureOfInterest",
        "featureType": "http://linked.data.gov.au/def/tern-cv/ecb855ed-50e1-4299-8491-861759ef40b7",
        "inDataset": "https://example.com/dataset/1"
      },
      "observedProperty": "https://linked.data.gov.au/def/test/dawe-cv/901bb17a-d1ff-4c4d-b5d8-bb2ac6f41903",
      "usedProcedure": "https://linked.data.gov.au/def/test/dawe-cv/37ed2dbb-b990-430c-9010-d0452588cf24",
      "hasResult": {
        "@id": "https://example.com/observation/behaviour/result",
        "isResultOf": "https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd",
        "vocabulary": "https://linked.data.gov.au/def/test/dawe-cv/f43074e8-6579-4fe1-8029-adb15e58c379",
        "@type": [
          "https://w3id.org/tern/ontologies/tern/IRI"
        ],
        "value": {
          "@id": "https://linked.data.gov.au/def/test/dawe-cv/881a2b9b-e363-5080-8659-69a7b5c4cf85"
        }
      },
      "phenomenonTime": {
        "@id": "https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd/phenomenonTime",
        "@type": "https://w3id.org/tern/ontologies/tern/Instant",
        "inXSDDateTimeStamp": {
          "@value": "2022-06-06T02:57:45.648Z",
          "@type": "http://www.w3.org/2001/XMLSchema#dateTime"
        }
      },
      "resultTime": "2022-06-06T02:57:45.648Z",
      "inDataset": "https://example.com/dataset/1"
    }
  ]
}""",
            "application/ld+json",
            """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix sosa: <http://www.w3.org/ns/sosa/> .
@prefix tern: <https://w3id.org/tern/ontologies/tern/> .
@prefix time: <http://www.w3.org/2006/time#> .
@prefix void: <http://rdfs.org/ns/void#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.com/feature-of-interest/66fa9efd-45f1-41d6-bef8-3c7e2e423f3d> a tern:FeatureOfInterest ;
    void:inDataset <https://example.com/dataset/1> ;
    tern:featureType <http://linked.data.gov.au/def/tern-cv/ecb855ed-50e1-4299-8491-861759ef40b7> .

<https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd> a tern:Observation ;
    void:inDataset <https://example.com/dataset/1> ;
    sosa:hasFeatureOfInterest <https://example.com/feature-of-interest/66fa9efd-45f1-41d6-bef8-3c7e2e423f3d> ;
    sosa:hasResult <https://example.com/observation/behaviour/result> ;
    sosa:observedProperty <https://linked.data.gov.au/def/test/dawe-cv/901bb17a-d1ff-4c4d-b5d8-bb2ac6f41903> ;
    sosa:phenomenonTime <https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd/phenomenonTime> ;
    sosa:resultTime "2022-06-06T02:57:45.648000+00:00"^^xsd:dateTime ;
    sosa:usedProcedure <https://linked.data.gov.au/def/test/dawe-cv/37ed2dbb-b990-430c-9010-d0452588cf24> .

<https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd/phenomenonTime> a tern:Instant ;
    time:inXSDDateTimeStamp "2022-06-06T02:57:45.648000+00:00"^^xsd:dateTime .

<https://example.com/observation/behaviour/result> a tern:IRI ;
    rdf:value <https://linked.data.gov.au/def/test/dawe-cv/881a2b9b-e363-5080-8659-69a7b5c4cf85> ;
    sosa:isResultOf <https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd> ;
    tern:vocabulary <https://linked.data.gov.au/def/test/dawe-cv/f43074e8-6579-4fe1-8029-adb15e58c379> .""",
            "text/turtle",
        ),
        (
            """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix sosa: <http://www.w3.org/ns/sosa/> .
@prefix tern: <https://w3id.org/tern/ontologies/tern/> .
@prefix time: <http://www.w3.org/2006/time#> .
@prefix void: <http://rdfs.org/ns/void#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.com/feature-of-interest/66fa9efd-45f1-41d6-bef8-3c7e2e423f3d> a tern:FeatureOfInterest ;
    void:inDataset <https://example.com/dataset/1> ;
    tern:featureType <http://linked.data.gov.au/def/tern-cv/ecb855ed-50e1-4299-8491-861759ef40b7> .

<https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd> a tern:Observation ;
    void:inDataset <https://example.com/dataset/1> ;
    sosa:hasFeatureOfInterest <https://example.com/feature-of-interest/66fa9efd-45f1-41d6-bef8-3c7e2e423f3d> ;
    sosa:hasResult <https://example.com/observation/behaviour/result> ;
    sosa:observedProperty <https://linked.data.gov.au/def/test/dawe-cv/901bb17a-d1ff-4c4d-b5d8-bb2ac6f41903> ;
    sosa:phenomenonTime <https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd/phenomenonTime> ;
    sosa:resultTime "2022-06-06T02:57:45.648000+00:00"^^xsd:dateTime ;
    sosa:usedProcedure <https://linked.data.gov.au/def/test/dawe-cv/37ed2dbb-b990-430c-9010-d0452588cf24> .

<https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd/phenomenonTime> a tern:Instant ;
    time:inXSDDateTimeStamp "2022-06-06T02:57:45.648000+00:00"^^xsd:dateTime .

<https://example.com/observation/behaviour/result> a tern:IRI ;
    rdf:value <https://linked.data.gov.au/def/test/dawe-cv/881a2b9b-e363-5080-8659-69a7b5c4cf85> ;
    sosa:isResultOf <https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd> ;
    tern:vocabulary <https://linked.data.gov.au/def/test/dawe-cv/f43074e8-6579-4fe1-8029-adb15e58c379> .""",
            "text/turtle",
            """[
  {
    "@id": "https://example.com/observation/behaviour/result",
    "@type": [
      "https://w3id.org/tern/ontologies/tern/IRI"
    ],
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": [
      {
        "@id": "https://linked.data.gov.au/def/test/dawe-cv/881a2b9b-e363-5080-8659-69a7b5c4cf85"
      }
    ],
    "http://www.w3.org/ns/sosa/isResultOf": [
      {
        "@id": "https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd"
      }
    ],
    "https://w3id.org/tern/ontologies/tern/vocabulary": [
      {
        "@id": "https://linked.data.gov.au/def/test/dawe-cv/f43074e8-6579-4fe1-8029-adb15e58c379"
      }
    ]
  },
  {
    "@id": "https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd",
    "@type": [
      "https://w3id.org/tern/ontologies/tern/Observation"
    ],
    "http://rdfs.org/ns/void#inDataset": [
      {
        "@id": "https://example.com/dataset/1"
      }
    ],
    "http://www.w3.org/ns/sosa/hasFeatureOfInterest": [
      {
        "@id": "https://example.com/feature-of-interest/66fa9efd-45f1-41d6-bef8-3c7e2e423f3d"
      }
    ],
    "http://www.w3.org/ns/sosa/hasResult": [
      {
        "@id": "https://example.com/observation/behaviour/result"
      }
    ],
    "http://www.w3.org/ns/sosa/observedProperty": [
      {
        "@id": "https://linked.data.gov.au/def/test/dawe-cv/901bb17a-d1ff-4c4d-b5d8-bb2ac6f41903"
      }
    ],
    "http://www.w3.org/ns/sosa/phenomenonTime": [
      {
        "@id": "https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd/phenomenonTime"
      }
    ],
    "http://www.w3.org/ns/sosa/resultTime": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2022-06-06T02:57:45.648000+00:00"
      }
    ],
    "http://www.w3.org/ns/sosa/usedProcedure": [
      {
        "@id": "https://linked.data.gov.au/def/test/dawe-cv/37ed2dbb-b990-430c-9010-d0452588cf24"
      }
    ]
  },
  {
    "@id": "https://example.com/feature-of-interest/66fa9efd-45f1-41d6-bef8-3c7e2e423f3d",
    "@type": [
      "https://w3id.org/tern/ontologies/tern/FeatureOfInterest"
    ],
    "http://rdfs.org/ns/void#inDataset": [
      {
        "@id": "https://example.com/dataset/1"
      }
    ],
    "https://w3id.org/tern/ontologies/tern/featureType": [
      {
        "@id": "http://linked.data.gov.au/def/tern-cv/ecb855ed-50e1-4299-8491-861759ef40b7"
      }
    ]
  },
  {
    "@id": "https://example.com/observation/behaviour/9465f3a5-8de0-4118-9090-c5cf56e50afd/phenomenonTime",
    "@type": [
      "https://w3id.org/tern/ontologies/tern/Instant"
    ],
    "http://www.w3.org/2006/time#inXSDDateTimeStamp": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2022-06-06T02:57:45.648000+00:00"
      }
    ]
  }
]""",
            "application/ld+json",
        ),
    ],
)
def test_convert(
    client: FlaskClient,
    url: str,
    source_data: str,
    source_format: str,
    target_data: str,
    target_format: str,
    logger,
):
    response: TestResponse = client.post(
        url,
        headers={"content-type": source_format, "accept": target_format},
        data=source_data,
    )

    assert response.status_code == 200

    if target_format == "application/ld+json":
        graph = Graph()
        graph.parse(data=response.text, format=target_format)

        target_graph = Graph()
        target_graph.parse(data=target_data, format=target_format)
    else:
        graph = Graph()
        graph.parse(data=response.text, format=target_format)

        target_graph = Graph()
        target_graph.parse(data=target_data, format=target_format)

    assert isomorphic(graph, target_graph)
    assert target_format in response.headers.get("content-type")
