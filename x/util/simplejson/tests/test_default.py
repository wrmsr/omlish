from unittest import TestCase

from ... import simplejson as json


class TestDefault(TestCase):
    def test_default(self):
        self.assertEqual(json.dumps(type, default=repr), json.dumps(repr(type)))
