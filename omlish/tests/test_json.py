from ..formats import json


def test_json():
    json.dumps_pretty({})
    json.dumps_compact({})
