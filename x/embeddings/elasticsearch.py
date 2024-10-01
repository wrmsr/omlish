"""
https://www.elastic.co/search-labs/blog/vector-search-implementation-guide-api-edition
"""
import os.path
import urllib.request

from omlish.docker.tests.services import ComposeServices
from omlish.formats import json


def _main():
    cs = ComposeServices(
        config_file_path=os.path.join(os.path.dirname(__file__), '../../docker/compose.yml'),
    )
    es_svc = cs.config().get_services()['elasticsearch']
    es_port = int(es_svc['ports'][0].split(':')[0])
    es_url = f'http://localhost:{es_port}'

    def send_request(path, *, method='POST', body):
        with urllib.request.urlopen(urllib.request.Request(
            f'{es_url}/{path}',
                method=method,
                headers={'Content-Type': 'application/json'},
                data=body.encode('utf-8') if body is not None else None,
        )) as resp:
            return resp.read()

    print(send_request(
        '_ingest/pipeline/vector_embedding_demo',
        method='PUT',
        body=json.dumps({
            "processors": [
                {
                    "inference": {
                        "field_map": {
                            "my_text": "text_field"
                        },
                        "model_id": "sentence-transformers__all-distilroberta-v1",
                        "target_field": "ml.inference.my_vector",
                        "on_failure": [
                            {
                                "append": {
                                    "field": "_source._ingest.inference_errors",
                                    "value": [
                                        {
                                            "message": (
                                                "Processor 'inference' in pipeline 'ml-inference-title-vector' failed "
                                                "with message '{{ _ingest.on_failure_message }}'"
                                            ),
                                            "pipeline": "ml-inference-title-vector",
                                            "timestamp": "{{{ _ingest.timestamp }}}"
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                },
                {
                    "set": {
                        "field": "my_vector",
                        "if": "ctx?.ml?.inference != null && ctx.ml.inference['my_vector'] != null",
                        "copy_from": "ml.inference.my_vector.predicted_value",
                        "description": "Copy the predicted_value to 'my_vector'"
                    }
                },
                {
                    "remove": {
                        "field": "ml.inference.my_vector",
                        "ignore_missing": True
                    }
                }
            ]
        }),
    ))

    print(send_request(
        '_index_template/my_vector_index',
        method='PUT',
        body=json.dumps({
            "index_patterns": [
                "my_vector_index-*"
            ],
            "priority": 1,
            "template": {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1,
                    "index.default_pipeline": "vector_embedding_demo"
                },
                "mappings": {
                    "properties": {
                        "my_vector": {
                            "type": "dense_vector",
                            "dims": 768,
                            "index": True,
                            "similarity": "dot_product"
                        },
                        "my_text": {
                            "type": "text"
                        }
                    },
                    "_source": {
                        "excludes": [
                            "my_vector"
                        ]
                    }
                }
            }
        }),
    ))

    print(send_request(
        'my_vector_index-01/_bulk?refresh=true',
        method='POST',
        body='\n'.join(map(json.dumps_compact, [
            {"index": {}},
            {"my_text": "Hey, careful, man, there's a beverage here!", "my_metadata": "The Dude"},
            {"index": {}},
            {
                "my_text": (
                    "I’m The Dude. So, that’s what you call me. You know, that or, uh, His Dudeness, or, uh, Duder, or "
                    "El Duderino, if you’re not into the whole brevity thing"
                ),
                "my_metadata": "The Dude",
            },
            {"index": {}},
            {
                "my_text": "You don't go out looking for a job dressed like that? On a weekday?",
                "my_metadata": "The Big Lebowski",
            },
            {"index": {}},
            {"my_text": "What do you mean brought it bowling, Dude? ", "my_metadata": "Walter Sobchak"},
            {"index": {}},
            {
                "my_text": (
                    "Donny was a good bowler, and a good man. He was one of us. He was a man who loved the outdoors... "
                    "and bowling, and as a surfer he explored the beaches of Southern California, from La Jolla to Leo "
                    "Carrillo and... up to... Pismo"
                ),
                "my_metadata": "Walter Sobchak",
            },
        ])),
    ))


if __name__ == '__main__':
    _main()
