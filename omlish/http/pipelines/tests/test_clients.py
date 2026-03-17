import unittest

from ...clients.base import HttpRequest
from .demos.clients import PipelineHttpClient


class TestClient(unittest.TestCase):
    def test_client(self):
        with PipelineHttpClient() as client:
            resp = client.stream_request(HttpRequest(
                'http://example.com/',
            ))
            print(resp)