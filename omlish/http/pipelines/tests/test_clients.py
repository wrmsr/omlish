# import unittest
#
# from ...clients.base import HttpRequest
# from .demos.clients import PipelineHttpClient
#
#
# class TestClient(unittest.TestCase):
#     def test_client(self):
#         with PipelineHttpClient() as client:
#             with client.stream_request(HttpRequest(
#                 'http://example.com/',
#             )) as resp:
#                 print(resp)
#                 print(resp.stream.readall())
#
#     def test_chunkserv(self):
#         with PipelineHttpClient() as client:
#             with client.stream_request(HttpRequest(
#                     'http://localhost.com:8080/',
#             )) as resp:
#                 print(resp)
#                 print(resp.stream.readall())
