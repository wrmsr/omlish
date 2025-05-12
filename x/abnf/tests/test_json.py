# import pytest
#
# from ..grammars import json
#
#
# @pytest.mark.parametrize('src', ["""
# {
#   "name": "Example Document",
#   "version": 1.0,
#   "active": true,
#   "tags": ["test", "json", "example"],
#   "metadata": {
#     "author": "Alice Smith",
#     "created": "2025-05-10T15:00:00Z",
#     "license": null
#   },
#   "items": [
#     {
#       "id": 1,
#       "name": "Widget A",
#       "price": 19.99,
#       "dimensions": {
#         "width": 5.5,
#         "height": 7.0,
#         "depth": 2.3
#       },
#       "tags": ["sale", "popular"]
#     },
#     {
#       "id": 2,
#       "name": "Widget B",
#       "price": 29.99,
#       "dimensions": {
#         "width": 6.0,
#         "height": 8.5,
#         "depth": 2.0
#       },
#       "tags": []
#     }
#   ],
#   "config": {
#     "debug": false,
#     "threshold": 0.75,
#     "features": {
#       "beta": true,
#       "experimental": ["x1", "x2"]
#     }
#   }
# }
# """
# ])
# def test_json(src):
#     node = json.Rule('json-text').parse_all(src)
#     print(node)
