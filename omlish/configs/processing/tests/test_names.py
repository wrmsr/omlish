# ruff: noqa: PT009
# @omlish-lite
import unittest

from ..matching import matched_config_rewrite
from ..names import build_config_named_children


class TestNames(unittest.TestCase):
    LST_ITEMS = [  # noqa
        dict(name='foo', thing='bar'),
        dict(name='baz', thing='qux'),
    ]

    DCT_ITEMS = dict(  # noqa
        foo=dict(thing='bar'),
        baz=dict(thing='qux'),
    )

    def test_names(self):
        self.assertEqual(
            build_config_named_children(self.DCT_ITEMS),
            self.LST_ITEMS,
        )

        self.assertEqual(
            build_config_named_children(self.LST_ITEMS),
            self.LST_ITEMS,
        )

    def test_rewrite(self):
        self.assertEqual(
            matched_config_rewrite(
                build_config_named_children,
                dict(
                    thingy='yes',
                    things=self.DCT_ITEMS,
                ),
                ('things',),
            ),
            dict(
                thingy='yes',
                things=self.LST_ITEMS,
            ),
        )

        self.assertEqual(
            matched_config_rewrite(
                build_config_named_children,
                dict(
                    thingy='yes',
                    things=self.LST_ITEMS,
                ),
                ('things',),
            ),
            dict(
                thingy='yes',
                things=self.LST_ITEMS,
            ),
        )
