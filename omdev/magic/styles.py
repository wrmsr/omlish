# ruff: noqa: UP006 UP007 UP045
import dataclasses as dc
import typing as ta


##


MAGIC_KEY_PREFIX = '@omlish-'


@dc.dataclass(frozen=True)
class MagicStyle:
    name: str

    exts: ta.FrozenSet[str] = frozenset()

    key_prefix: str = MAGIC_KEY_PREFIX

    line_prefix: ta.Optional[str] = None
    block_prefix_suffix: ta.Optional[ta.Tuple[str, str]] = None


PY_MAGIC_STYLE = MagicStyle(
    name='py',
    exts=frozenset([
        'py',
    ]),
    line_prefix='# ',
)


C_MAGIC_STYLE = MagicStyle(
    name='c',
    exts=frozenset([
        'c',
        'cc',
        'cpp',
        'cu',
    ]),
    line_prefix='// ',
    block_prefix_suffix=('/* ', '*/'),
)
