import threading
import typing as ta

from .annotations import TypeAnnotations
from .reflector import ForwardRefResolver
from .reflector import TypeReflector
from .typekeys import TypeKeys
from .universe import TypeUniverse
from .universe import or_global_universe


##


@ta.final
class Api:
    def __init__(
            self,
            universe: TypeUniverse | None = None,
            *,
            forward_ref_resolver: ForwardRefResolver | None = None,
    ) -> None:
        super().__init__()

        self._universe: ta.Final = or_global_universe(universe)

        self._lock: ta.Final = threading.RLock()

        self._reflector: ta.Final = TypeReflector(
            forward_ref_resolver=forward_ref_resolver,
            universe=self._universe,
            lock=self._lock,
        )

        self._keys: ta.Final = TypeKeys(
            lock=self._lock,
        )

        self._annotations: ta.Final = TypeAnnotations(
            reflector=self._reflector,
            lock=self._lock,
        )

    @property
    def universe(self) -> TypeUniverse:
        return self._universe

    @property
    def reflector(self) -> TypeReflector:
        return self._reflector

    @property
    def keys(self) -> TypeKeys:
        return self._keys

    @property
    def annotations(self) -> TypeAnnotations:
        return self._annotations


##


_GLOBAL_API: ta.Final = Api()


def global_api() -> Api:
    return _GLOBAL_API


def or_global_api(api: Api | None) -> Api:
    return _GLOBAL_API if api is None else api
