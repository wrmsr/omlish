# ruff: noqa: UP006 UP007
import collections
import dataclasses as dc
import typing as ta

from .providers.base import InterpProvider
from .types import Interp
from .types import InterpSpecifier
from .types import InterpVersion


@dc.dataclass(frozen=True)
class InterpResolverProviders:
    providers: ta.Sequence[ta.Tuple[str, InterpProvider]]


class InterpResolver:
    def __init__(
            self,
            providers: InterpResolverProviders,
    ) -> None:
        super().__init__()

        self._providers: ta.Mapping[str, InterpProvider] = collections.OrderedDict(providers.providers)

    async def _resolve_installed(self, spec: InterpSpecifier) -> ta.Optional[ta.Tuple[InterpProvider, InterpVersion]]:
        lst = [
            (i, si)
            for i, p in enumerate(self._providers.values())
            for si in await p.get_installed_versions(spec)
            if spec.contains(si)
        ]

        slst = sorted(lst, key=lambda t: (-t[0], t[1].version))
        if not slst:
            return None

        bi, bv = slst[-1]
        bp = list(self._providers.values())[bi]
        return (bp, bv)

    async def resolve(
            self,
            spec: InterpSpecifier,
            *,
            install: bool = False,
    ) -> ta.Optional[Interp]:
        tup = await self._resolve_installed(spec)
        if tup is not None:
            bp, bv = tup
            return await bp.get_installed_version(bv)

        if not install:
            return None

        tp = list(self._providers.values())[0]  # noqa

        sv = sorted(
            [s for s in await tp.get_installable_versions(spec) if s in spec],
            key=lambda s: s.version,
        )
        if not sv:
            return None

        bv = sv[-1]
        return await tp.install_version(bv)

    async def list(self, spec: InterpSpecifier) -> None:
        print('installed:')
        for n, p in self._providers.items():
            lst = [
                si
                for si in await p.get_installed_versions(spec)
                if spec.contains(si)
            ]
            if lst:
                print(f'  {n}')
                for si in lst:
                    print(f'    {si}')

        print()

        print('installable:')
        for n, p in self._providers.items():
            lst = [
                si
                for si in await p.get_installable_versions(spec)
                if spec.contains(si)
            ]
            if lst:
                print(f'  {n}')
                for si in lst:
                    print(f'    {si}')
