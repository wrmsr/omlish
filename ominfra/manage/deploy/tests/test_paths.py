# ruff: noqa: UP006 UP007
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
            'ab/@app/cd',
            'ab/@app/cd/',
            'ab/@app/cd/foo',
            'ab/@app/cd/@deploy.foo',
        ]:
            print()
            print(s)
            dp = DeployPath.parse(s)
            print(dp)
            print(dp.render())
            print(json_dumps_pretty(msh.marshal_obj(dp)))

        for s in [
            'ab/@app/cd/@app.foo',
            'ab/@deploy/cd/@app.foo',
            'ab/@deploy',
        ]:
            with self.assertRaises(DeployPathError):
                DeployPath.parse(s)
