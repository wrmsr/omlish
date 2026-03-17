"""
TODO:
 - axes:
   - flow
   - ssl : 'https://example.com/'
   - gzip decompress : 'https://httpbingo.org/gzip'
   - gzip compressed
"""
import unittest

from ...base import HttpClientRequest
from ..sync import IoPipelineHttpClient


class TestSyncClient(unittest.TestCase):
    def test_simple(self):
        with IoPipelineHttpClient() as client:
            with client.stream_request(HttpClientRequest(
                'http://example.com/',
            )) as resp:
                print(resp)
                print(resp.stream.read())

    def test_ssl(self):
        with IoPipelineHttpClient() as client:
            with client.stream_request(HttpClientRequest(
                    'https://example.com/',
            )) as resp:
                print(resp)
                print(resp.stream.read())

    def test_gzip(self):
        with IoPipelineHttpClient() as client:
            with client.stream_request(HttpClientRequest(
                    'http://example.com/gzip',
            )) as resp:
                print(resp)
                print(resp.stream.read())

    def test_ssl_gzip(self):
        with IoPipelineHttpClient() as client:
            with client.stream_request(HttpClientRequest(
                    'https://example.com/gzip',
            )) as resp:
                print(resp)
                print(resp.stream.read())
