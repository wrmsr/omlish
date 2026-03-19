# fmt: off
# flake8: noqa: E131
import json

from omlish import collections as col
from omlish.algorithm.prefixes import min_unique_prefix_len

from .... import _fieldhash as fh
from ..collection import ToolPermissionRules
from ..fs import GlobFsToolPermissionMatcher
from ..types import ToolPermissionRule
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

    for _ in range(2):
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

    for _ in range(2):
        assert fh.digest_field_hash(rules) == 'b4a91821704c1616494f5036a238a2b9782b3f41'

    dct0 = rules.by_digest
    print(dct0)

    mpl = max(min_unique_prefix_len(list(dct0)), 4)
    print(mpl)

    dct1: dict[str, ToolPermissionRule] = col.make_map(((k[:mpl], v) for k, v in dct0.items()), strict=True)
    print(dct1)
