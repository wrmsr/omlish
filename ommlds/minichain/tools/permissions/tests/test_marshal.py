import json

from omlish import marshal as msh

from ..fs import GlobFsToolPermissionMatcher
from ..types import ToolPermissionRule
from ..types import ToolPermissionState
from ..url import RegexUrlToolPermissionMatcher


def test_marshal():
    rules = [
        ToolPermissionRule(
            RegexUrlToolPermissionMatcher('https://google.com/.*'),
            ToolPermissionState.DENY,
        ),
        ToolPermissionRule(
            GlobFsToolPermissionMatcher('**/*.py'),
            ToolPermissionState.ASK,
        ),
    ]

    j = json.dumps(msh.marshal(rules))
    print(j)
