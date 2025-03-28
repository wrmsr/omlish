import dataclasses as dc
import itertools
import os.path
import textwrap
import typing as ta


##


class CodeGen:
    def __init__(self, iface_names: ta.Sequence[str]) -> None:
        super().__init__()

        if isinstance(iface_names, str):
            raise TypeError(iface_names)
        in_tup = tuple(iface_names)
        for ic in in_tup:
            if not isinstance(ic, str) or not ic:
                raise ValueError(ic)
        if len(in_tup) < 2:
            raise ValueError(in_tup)

        self._iface_names = in_tup

        self._bases = self._make_bases(in_tup)

    #

    @classmethod
    def _name_base(cls, *iface_names: str) -> str:
        return ''.join(iface_name[:-2] for iface_name in iface_names) + 'Kv'

    @dc.dataclass(frozen=True)
    class Base:
        name: str
        ifaces: tuple[str, ...]
        supers: tuple[str, ...]

    @classmethod
    def _make_bases(cls, iface_names: ta.Sequence[str]) -> ta.Mapping[str, Base]:
        dct: dict[str, CodeGen.Base] = {}

        iface_tup_lsts_by_len: dict[int, list[tuple[str, ...]]] = {}
        for iface_prod in itertools.product(*[(None, ic) for ic in iface_names]):
            iface_tup = tuple(ic for ic in iface_prod if ic is not None)
            iface_tup_lsts_by_len.setdefault(len(iface_tup), []).append(iface_tup)

        for iface_tup in itertools.chain.from_iterable(iface_tup_lsts_by_len.values()):
            if len(iface_tup) < 2:
                continue

            name = cls._name_base(*iface_tup)

            super_bases = []
            for super_iface_tup in iface_tup_lsts_by_len[len(iface_tup) - 1]:
                if set(super_iface_tup) - set(iface_tup):
                    continue
                super_base = cls._name_base(*super_iface_tup)
                super_bases.append(super_base)

            base = CodeGen.Base(
                name,
                ifaces=iface_tup,
                supers=tuple(super_bases),
            )
            dct[name] = base

        return dct

    #

    @dc.dataclass(frozen=True)
    class Section:
        lines: ta.Sequence[str]
        exports: ta.Sequence[str] = ()

    def _gen_bases_section(self) -> Section:
        lines = []
        exports = []

        for i, b in enumerate(self._bases.values()):
            exports.append(b.name)

            if i:
                lines.append('\n')

            super_lines = [
                *[super_base + '[K, V]' for super_base in reversed(b.supers)],
                'Kv[K, V]',
                'lang.Abstract',
                'ta.Generic[K, V]',
            ]

            lines.extend([
                f'class {b.name}(  # noqa',
                *[f'    {l},' for l in super_lines],
                '):',
                '    pass',
            ])

        lines.extend([
            '\n',
            f'FullKv: ta.TypeAlias = {exports[-1]}[K, V]',
        ])
        exports.append('FullKv')

        return CodeGen.Section(
            lines,
            exports=exports,
        )

    def _gen_bases_by_mro_section(self) -> Section:
        return CodeGen.Section(
            lines=[
                'KV_BASES_BY_MRO: ta.Mapping[tuple[type[Kv], ...], type[Kv]] = {',
                *[
                    f'    ({ic},): {ic},'
                    for ic in reversed(self._iface_names)
                ],
                *[
                    f'    ({", ".join(b.ifaces)}): {b.name},'
                    for b in self._bases.values()
                ],
                '}',
            ],
            exports=['KV_BASES_BY_MRO'],
        )

    def _gen_kv_to_kv_func_section(self) -> Section:
        return CodeGen.Section(
            lines=[
                # 'class KvToKvFunc(ta.Protocol[P, KF, VF, KT, VT]):',
                'class KvToKvFunc(ta.Protocol[KF, VF, KT, VT]):',
                *itertools.chain.from_iterable(
                    [
                        f'    @ta.overload',
                        f'    def __call__(',
                        f'        self,',
                        f'        kv: {bn}[KF, VF],',
                        # f'        *args: P.args,',
                        # f'        **kwargs: P.kwargs,',
                        f'        *args: ta.Any,',
                        f'        **kwargs: ta.Any,',
                        f'    ) -> {bn}[KT, VT]: ...',
                        f'',
                    ]
                    for bn in [
                        *reversed(list(self._bases)),
                        *self._iface_names,
                    ]
                ),
                '    def __call__(self, kv, *args, **kwargs): ...',
            ],
            exports=['KvToKvFunc'],
        )

    def _gen_install_section(self) -> Section:
        return CodeGen.Section([
            'from . import interfaces as _interfaces  # noqa',
            '',
            '_interfaces._KV_BASES_BY_MRO = KV_BASES_BY_MRO  # noqa',
        ])

    #

    _HEADER_TEXT = textwrap.dedent('''
    # @omlish-generated
    """
    Note: This is all just a hacky workaround for python's lack of intersection types. See:

      https://github.com/python/typing/issues/213

    """
    ''').strip()

    _HEADER_GENERAL_IMPORTS: ta.Sequence[str] = [
        'import typing as ta',
        '',
        'from omlish import lang',
    ]

    _HEADER_TYPE_DEFS: ta.Sequence[str] = [
        "K = ta.TypeVar('K')",
        "V = ta.TypeVar('V')",
        '',
        "KF = ta.TypeVar('KF')",
        "KT = ta.TypeVar('KT')",
        '',
        "VF = ta.TypeVar('VF')",
        "VT = ta.TypeVar('VT')",
        # '',
        # "P = ta.ParamSpec('P')",
    ]

    def _gen_header_section(self) -> Section:
        return CodeGen.Section([
            self._HEADER_TEXT,
            *self._HEADER_GENERAL_IMPORTS,
            '',
            *[
                f'from .interfaces import {n}'
                for n in sorted([
                    'Kv',
                    *self._iface_names,
                ])
            ],
            '\n',
            *self._HEADER_TYPE_DEFS,
        ])

    #

    _NO_MAIN_SECTION = Section([
        "if __name__ == '__main__':",
        "    raise RuntimeError('Must not be run as __main__ - would produce duplicate kv base classes.')",
    ])

    #

    def _gen_all_section(self, sections: ta.Iterable[Section]) -> Section:
        lines = [
            '__all__ = [  # noqa',
        ]
        for i, sec in enumerate(sections):
            if not sec.exports:
                continue
            if i:
                lines.append('')
            lines.extend([
                f'    {n!r},'
                for n in sec.exports
            ])
        lines.append(
            ']',
        )

        return CodeGen.Section(lines)

    #

    _SECTION_DIVIDER: str = '\n'.join([
        '\n',
        '##',
        '\n',
    ])

    def gen(self) -> str:
        header_section = self._gen_header_section()

        content_sections = [
            self._gen_bases_section(),
            self._gen_bases_by_mro_section(),
            self._gen_kv_to_kv_func_section(),
            self._gen_install_section(),
        ]

        all_section = self._gen_all_section(content_sections)

        sections = [
            header_section,
            self._NO_MAIN_SECTION,
            all_section,
            *content_sections,
        ]

        lines = []
        for i, sec in enumerate(sections):
            if i:
                lines.append(self._SECTION_DIVIDER)
            lines.extend(sec.lines)

        lines.append('')
        return '\n'.join(lines)


##


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('iface_names', metavar='iface-name', nargs='*')
    parser.add_argument('-w', '--write', action='store_true')
    parser.add_argument('-q', '--quiet', action='store_true')

    args = parser.parse_args()

    iface_names: ta.Sequence[str]
    if args.iface_names:
        iface_names = args.iface_names

    else:
        from .interfaces import KV_INTERFACES
        iface_names = [ic.__name__ for ic in KV_INTERFACES]

    src = CodeGen(iface_names).gen()

    if not args.quiet:
        print(src)

    if args.write:
        with open(os.path.join(os.path.dirname(__file__), 'bases.py') ,'w') as f:
            f.write(src)


if __name__ == '__main__':
    _main()
