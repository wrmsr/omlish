# ruff: noqa: UP006
import abc
import collections
import typing as ta

from omlish.lite.reflect import deep_subclasses

from .providers import InterpProvider
from .providers import RunningInterpProvider
from .pyenv import PyenvInterpProvider
from .system import SystemInterpProvider
from .types import Interp
from .types import InterpSpecifier


INTERP_PROVIDER_TYPES_BY_NAME: ta.Mapping[str, ta.Type[InterpProvider]] = {
    cls.name: cls for cls in deep_subclasses(InterpProvider) if abc.ABC not in cls.__bases__  # type: ignore
}


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


DEFAULT_INTERP_RESOLVER = InterpResolver([(p.name, p) for p in [
    # pyenv is preferred to system interpreters as it tends to have more support for things like tkinter
    PyenvInterpProvider(),

    RunningInterpProvider(),

    SystemInterpProvider(),
]])
