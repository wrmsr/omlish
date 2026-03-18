from ..fs import GlobFsToolPermissionMatcher
from ..types import ToolPermissionRule
from ..types import ToolPermissionRules
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

    v = rules._field_hash()  # noqa
    print(v)
