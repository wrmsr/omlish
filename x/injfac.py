import abc
import typing as ta

from omlish import check
from omlish import lang
from omlish.inject.elements import CollectedElements
from omlish.inject.elements import Elemental
from omlish.inject.elements import as_elements
from omlish.inject.elements import collect_elements


T = ta.TypeVar('T')


##


class _InjectorCreator(lang.Abstract, ta.Generic[T]):
    @ta.overload
    def __call__(self, es: CollectedElements, /) -> T: ...

    @ta.overload
    def __call__(self, *es: Elemental) -> T: ...

    def __call__(self, arg0, *argv):
        ce: CollectedElements
        if isinstance(arg0, CollectedElements):
            check.arg(not argv)
            ce = arg0
        else:
            ce = collect_elements(as_elements(arg0, *argv))
        return self._create(ce)

    @abc.abstractmethod
    def _create(self, ce: CollectedElements) -> T:
        raise NotImplementedError
