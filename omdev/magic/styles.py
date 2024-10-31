import dataclasses as dc


MAGIC_KEY_PREFIX = '@omlish-'


@dc.dataclass(frozen=True)
class MagicStyle:
    name: str

    exts: frozenset[str] = frozenset()

    key_prefix: str = MAGIC_KEY_PREFIX

    line_prefix: str | None = None
    block_prefix_suffix: tuple[str, str] | None = None


PY_MAGIC_STYLE = MagicStyle(
    name='py',
    exts=frozenset(['py']),
    line_prefix='# ',
)


C_MAGIC_STYLE = MagicStyle(
    name='c',
    exts=frozenset(['c', 'cc', 'cpp']),
    line_prefix='// ',
    block_prefix_suffix=('/* ', '*/'),
)
