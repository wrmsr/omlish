# ruff: noqa: PT009
# @omlish-lite
import unittest

from ..inheritance import build_config_inherited_values


class TestInheritance(unittest.TestCase):
    def test_build(self):
        i = dict(
            _a=dict(a='a!'),
            _b=dict(b='b!'),

            c=dict(c='c!', _inherits=['_a']),
            d=dict(d='d!', _inherits=['_b']),
            e=dict(e='e!'),
            f=dict(f='f!', _inherits=['_a', '_b']),
        )

        o = {
            k: v
            for k, v in build_config_inherited_values(i, inherits_key='_inherits').items()  # type: ignore
            if not k.startswith('_')
        }

        e = dict(
            c=dict(c='c!', a='a!'),
            d=dict(d='d!', b='b!'),
            e=dict(e='e!'),
            f=dict(f='f!', a='a!', b='b!'),
        )

        self.assertEqual(o, e)
