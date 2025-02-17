# ruff: noqa: PT009
# @omlish-lite
import unittest

from ..mangle import mangle_path
from ..mangle import unmangle_path


class TestMangle(unittest.TestCase):
    def test_mangle(self):
        test_paths = [
            '/home/user/docs/file.txt',
            '/var/log/nginx/access.log',
            '/path/with_underscores/file',
            '/single/',
            '/',
        ]

        for path in test_paths:
            mangled = mangle_path(path)
            unmangled = unmangle_path(mangled)
            self.assertEqual(unmangled, path)
