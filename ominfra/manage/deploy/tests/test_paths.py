# ruff: noqa: UP006 UP007
from omlish.lite import marshal as msh
from omlish.lite.json import json_dumps_pretty

from ..paths import DeployPathDir


def test_marshal():
    dp = DeployPath([
        DeployConstDir('logs'),
        DeploySpecDir(),
    ])

    print()
    print(dp)
    print(dp.render())
    print(json_dumps_pretty(msh.marshal_obj(dp)))
