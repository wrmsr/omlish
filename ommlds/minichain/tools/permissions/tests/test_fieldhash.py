# fmt: off
# flake8: noqa: E131
import json

import pytest

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

    rds = [
        '28cb135ac5b3328cec14a38efbc2ce21e02aaf32',
        '833f94dd220336fac525cc6cb0b31e5d0f8f6a02',
        '1f04d07271fd8c48c2699afc99563101efdfcf40',
        '48662e3d2705d8d635c0142d337ff02c08d47365',
    ]
    assert list(dct0) == rds

    assert rules[rds[1]] is rules[1]

    dct1 = rules.by_min_digest
    assert dct1 == {k[:3]: v for k, v in dct0.items()}

    with pytest.raises(KeyError):
        rules['28']  # noqa
    assert rules['28c'] is rules[0]
    with pytest.raises(KeyError):
        rules['28d']  # noqa
    assert rules['1f0'] is rules[2]

    assert rules['28cb13'] is rules[0]
    with pytest.raises(KeyError):
        rules['28cbd']  # noqa
    assert rules['1f04d07271fd'] is rules[2]
