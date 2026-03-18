# flake8: noqa: E131
import json

from .. import _fieldhash as fh
from ..fs import GlobFsToolPermissionMatcher
from ..types import ToolPermissionRule
from ..types import ToolPermissionRules
from ..types import ToolPermissionState
from ..url import RegexUrlToolPermissionMatcher


def test_field_hash():
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

    r = fh.render_field_hash(rules)

    assert r == (
        '{'
            '"rules":{'
                '"rules":['

                    '{'
                        '"rule":{'
                            '"matcher":{'
                                '"regex_url":{'
                                    '"pat":"https://google.com/.*",'
                                    '"methods":null'
                                '}'
                            '},'
                            '"result":"DENY"'
                        '}'
                    '},'

                    '{'
                        '"rule":{'
                            '"matcher":{'
                                '"regex_url":{'
                                    '"pat":"https://baidu.com/.*",'
                                    '"methods":["POST"]'
                                '}'
                            '},'
                            '"result":"DENY"'
                        '}'
                    '},'

                    '{'
                        '"rule":{'
                            '"matcher":{'
                                '"glob_fs":{'
                                    '"glob":"**/*.py",'
                                    '"modes":null'
                                '}'
                            '},'
                            '"result":"ASK"'
                        '}'
                    '},'

                    '{'
                        '"rule":{'
                            '"matcher":{'
                                '"glob_fs":{'
                                    '"glob":"**/*.exe",'
                                    '"modes":["r"]'
                                '}'
                            '},'
                            '"result":"DENY"'
                        '}'
                    '}'

                ']'
            '}'
        '}'
    )

    u = json.loads(r)

    assert u == {
        'rules': {
            'rules': [
                {
                    'rule': {
                        'matcher': {
                            'regex_url': {
                                'pat': 'https://google.com/.*',
                                'methods': None,
                            },
                        },
                        'result': 'DENY',
                    },
                },
                {
                    'rule': {
                        'matcher': {
                            'regex_url': {
                                'pat': 'https://baidu.com/.*',
                                'methods': ['POST'],
                            },
                        },
                        'result': 'DENY',
                    },
                },
                {
                    'rule': {
                        'matcher': {
                            'glob_fs': {
                                'glob': '**/*.py',
                                'modes': None,
                            },
                        },
                        'result': 'ASK',
                    },
                },
                {
                    'rule': {
                        'matcher': {
                            'glob_fs': {
                                'glob': '**/*.exe',
                                'modes': ['r'],
                            },
                        },
                        'result': 'DENY',
                    },
                },
            ],
        },
    }
