import threading
import typing as ta

from .annotations import TypeAnnotations
from .typekeys import TypeKeys
from .reflector import TypeReflector
from .universe import TypeUniverse
from .universe import or_default_universe
from .reflector import ForwardRefResolver


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

        self._universe: ta.Final = or_default_universe(universe)

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


_DEFAULT_API: ta.Final = Api()


def default_api() -> Api:
    return _DEFAULT_API


def or_default_api(api: Api | None) -> Api:
    return _DEFAULT_API if api is None else api
