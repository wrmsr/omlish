# ruff: noqa: PT009 PT027 UP006 UP007
import itertools
import unittest

from omlish.lite import marshal as msh
from omlish.lite.json import json_dumps_pretty

from ..paths import DeployPath
from ..paths import DeployPathError


class TestMarshal(unittest.TestCase):
    def test_marshal(self):
        for s in [
            'abc',
            'abc/',
            'abc/def',
            'abc/def/',

            'ab/@app/cd',
            'ab/@app/cd/',
            'ab/@app/cd/foo',
            'ab/@app/cd/@tag.foo',

            #

            *itertools.chain.from_iterable([
                f'{pfx}/apps/@app',
                f'{pfx}/conf/@conf',
            ] for pfx in [
                'current',
                'deploying',
            ]),

            'tags/apps/@app--@tag/conf/',
            'tags/apps/@app--@tag/git/',
            'tags/apps/@app--@tag/venv/',

            'tags/conf/@conf--@app--@tag/',
        ]:
            print()
            print(s)
            dp = DeployPath.parse(s)
            print(dp)
            print(dp.render())
            # self.assertEqual(dp.render(), s)
            # print(json_dumps_pretty(msh.marshal_obj(dp)))

        #

        self.assertEqual(
            DeployPath.parse('ab/@app/cd/@tag.foo').render({'app': 'foo', 'tag': 'bar'}),
            'ab/foo/cd/bar.foo',
        )

        #

        for s in [
            'ab/@app/cd/@app.foo',
            'ab/@tag/cd/@app.foo',
            'ab/@tag',
        ]:
            with self.assertRaises(DeployPathError):
                DeployPath.parse(s)
