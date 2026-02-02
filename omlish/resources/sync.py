import contextlib
import typing as ta

from .. import check
from .. import lang
from .base import BaseResourceManaged
from .base import BaseResources
from .base import ResourcesRef
from .errors import ResourcesRefNotRegisteredError


U = ta.TypeVar('U')


##


@ta.final
class Resources(
    BaseResources[None],
    lang.Final,
):
    def __init__(
            self,
            *,
            init_ref: ResourcesRef | None = None,
            no_autoclose: bool = False,
    ) -> None:
        super().__init__(
            init_ref=init_ref,
            no_autoclose=no_autoclose,
        )

        self._es = contextlib.ExitStack()

    def init(self) -> None:
        self._es.__enter__()

        self._init_debug()

    #

    @classmethod
    def new(cls, **kwargs: ta.Any) -> ta.ContextManager['Resources']:
        @contextlib.contextmanager
        def inner():
            init_ref = BaseResources._InitRef()  # noqa

            res = Resources(init_ref=init_ref, **kwargs)

            res.init()

            try:
                yield res

            finally:
                res.remove_ref(init_ref)

        return inner()

    @classmethod
    def or_new(
            cls,
            resources: ta.Optional['Resources'],
            **kwargs: ta.Any,
    ) -> ta.ContextManager['Resources']:
        if resources is None:
            return cls.new(**kwargs)

        @contextlib.contextmanager
        def inner():
            yield resources

        return inner()

    #

    def remove_ref(self, ref: ResourcesRef) -> None:
        check.isinstance(ref, ResourcesRef)

        try:
            self._refs.remove(ref)

        except KeyError:
            raise ResourcesRefNotRegisteredError(ref) from None

        if not self._no_autoclose and not self._refs:
            self.close()

    #

    def enter_context(self, cm: ta.ContextManager[U]) -> U:
        check.state(not self._closed)

        return self._es.enter_context(cm)

    #

    def new_managed(self, v: U) -> 'ResourceManaged[U]':
        return ResourceManaged(v, self)  # noqa

    #

    def close(self) -> None:
        try:
            self._es.__exit__(None, None, None)
        finally:
            self._closed = True


@ta.final
class ResourceManaged(
    BaseResourceManaged[U, Resources],
    ta.ContextManager[U],
    lang.Final,
):
    def __enter__(self) -> U:
        check.state(self._state == 'new')
        self._state = 'entered'

        self._init_debug()

        return self._v

    def __exit__(self, exc_type, exc_val, exc_tb):
        check.state(self._state == 'entered')
        self._state = 'exited'

        self._resources.remove_ref(self)
