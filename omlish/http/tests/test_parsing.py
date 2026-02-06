# @omlish-lite
import unittest

from ..parsing import HttpRequestParser


class TestParsing(unittest.TestCase):
    def test_parsing(self):
        req = HttpRequestParser().parse_full(
            b'GET / HTTP/1.1\r\n'
            b'Host: example.com\r\n'
            b'\r\n',
        )
        print(req)
