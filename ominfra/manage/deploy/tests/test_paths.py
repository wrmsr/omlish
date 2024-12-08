# ruff: noqa: UP006 UP007
from omlish.lite import marshal as msh
from omlish.lite.json import json_dumps_pretty

from ..paths import DeployPath


def test_marshal():
    for s in [
        'abc',
        'abc/',
        'ab/@/cd',
        'ab/@/cd/',
        'ab/@/cd/foo',
        'ab/@/cd/@.foo',
    ]:
        print()
        print(s)
        dp = DeployPath.parse(s)
        print(dp)
        print(dp.render())
        print(json_dumps_pretty(msh.marshal_obj(dp)))
