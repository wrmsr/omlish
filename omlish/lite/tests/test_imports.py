# ruff: noqa: PT009 UP006 UP007
import unittest

from ..imports import import_attr


class TesTImportAttr(unittest.TestCase):
    def test_import_attr(self):
        dotted_path = __package__.rpartition('.')[0] + '.imports.import_attr.__name__'
        name = import_attr(dotted_path)
        self.assertEqual(name, 'import_attr')
