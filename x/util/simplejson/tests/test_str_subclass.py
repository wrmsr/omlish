from unittest import TestCase

from ... import simplejson as json


# Tests for issue demonstrated in https://github.com/simplejson/simplejson/issues/144
class WonkyTextSubclass(str):
    def __getslice__(self, start, end):
        return self.__class__('not what you wanted!')


class TestStrSubclass(TestCase):
    def test_dump_load(self):
        for s in ['', '"hello"', 'text', '\u005c']:
            self.assertEqual(
                s, json.loads(json.dumps(WonkyTextSubclass(s))),
            )

            self.assertEqual(
                s,
                json.loads(
                    json.dumps(WonkyTextSubclass(s), ensure_ascii=False),
                ),
            )
