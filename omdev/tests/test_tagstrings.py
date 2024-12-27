# ruff: noqa: PT009
import unittest

from ..tagstrings import TagString
from ..tagstrings import TagStringCatalog
from ..tagstrings import TagStringSet


class TestTagStrings(unittest.TestCase):
    def test_tag_strings(self) -> None:
        platform_tag = TagString.new_hierarchy(
            'platform',
            {
                'darwin': {},
                'linux': {
                    'ubuntu': {
                        '22': {},
                        '24': {},
                    },
                    'amazon': {},
                },
            },
        )

        throttle_tag = TagString.new_str(
            'throttle',
            [
                'cpu',
                'disk',
                'network',
            ],
            set=True,
        )

        profile_tag = TagString.new_str(
            'profile',
            [
                'dev',
                'server',
            ],
        )

        tag_catalog = TagStringCatalog([
            platform_tag,
            throttle_tag,
            profile_tag,
        ])

        o = tag_catalog.parse_set(
            'throttle:cpu',
            'throttle:disk',
            'platform:linux:ubuntu:22',
        )

        e = TagStringSet({
            'throttle': frozenset({'disk', 'cpu'}),
            'platform': frozenset({('linux',), ('linux', 'ubuntu', '22'), ('linux', 'ubuntu')}),
        })

        self.assertEqual(o, e)
