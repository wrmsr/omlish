from omlish import marshal as msh
from omlish.formats import json

from ..collection import ToolPermissionRules
from ..fs import GlobFsToolPermissionMatcher
from ..types import ToolPermissionRule
from ..types import ToolPermissionState
from ..url import RegexUrlToolPermissionMatcher


def test_marshal():
    rules = ToolPermissionRules([
        ToolPermissionRule(
            RegexUrlToolPermissionMatcher('https://google.com/.*'),
            ToolPermissionState.DENY,
        ),
        ToolPermissionRule(
            RegexUrlToolPermissionMatcher('https://baidu.com/.*', methods=['POST']),
            ToolPermissionState.DENY,
        ),
        ToolPermissionRule(
            GlobFsToolPermissionMatcher('**/*.py'),
            ToolPermissionState.ASK,
        ),
        ToolPermissionRule(
            GlobFsToolPermissionMatcher('**/*.exe', modes=['r']),
            ToolPermissionState.DENY,
        ),
    ])

    j = json.dumps_pretty(msh.marshal(rules))
    print(j)
