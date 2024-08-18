import collections
import typing as ta

from .providers.base import InterpProvider
from .providers.base import RunningInterpProvider
from .providers.pyenv import PyenvInterpProvider
from .providers.system import SystemInterpProvider
from .providers.types import Interp
from .providers.types import InterpSpecifier


class InterpResolver:
    def __init__(
            self,
            providers: ta.Sequence[ta.Tuple[str, InterpProvider]],
    ) -> None:
        super().__init__()
        self._providers: ta.Mapping[str, InterpProvider] = collections.OrderedDict(providers)

    def resolve(self, spec: InterpSpecifier) -> Interp:
        lst = [
            (i, si)
            for i, p in enumerate(self._providers.values())
            for si in p.get_installed_versions(spec)
            if spec.contains(si)
        ]
        best = sorted(lst, key=lambda t: (-t[0], t[1]))[-1]
        bi, bv = best
        bp = list(self._providers.values())[bi]
        return bp.get_installed_version(bv)

    def list(self, spec: InterpSpecifier) -> None:
        print('installed:')
        for n, p in self._providers.items():
            lst = [
                si
                for si in p.get_installed_versions(spec)
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
                for si in p.get_installable_versions(spec)
                if spec.contains(si)
            ]
            if lst:
                print(f'  {n}')
                for si in lst:
                    print(f'    {si}')


DEFAULT_INTERP_RESOLVER = InterpResolver([
    ('running', RunningInterpProvider()),
    ('pyenv', PyenvInterpProvider()),
    ('system', SystemInterpProvider()),
])
