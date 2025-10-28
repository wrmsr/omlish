import abc
import typing as ta

from omlish import lang

from ...configs import Config


T = ta.TypeVar('T')


##


class BackendCatalog(lang.Abstract):
    class Backend(ta.NamedTuple):
        factory: ta.Callable[..., ta.Any]
        configs: ta.Sequence[Config] | None

    @abc.abstractmethod
    def get_backend(self, service_cls: type[T], name: str) -> Backend:
        raise NotImplementedError

    def new_backend(
            self,
            service_cls: ta.Any,
            name: str,
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> ta.Any:
        be = self.get_backend(service_cls, name)
        return be.factory(*be.configs or [], *args, **kwargs)

    # #
    #
    # class Bound(lang.Final, ta.Generic[T]):
    #     def __init__(self, catalog: 'BackendCatalog', service_cls: ta.Any) -> None:
    #         super().__init__()
    #
    #         self._catalog = catalog
    #         self._service_cls = service_cls
    #
    #     def get_backend(self, name: str, *args: ta.Any, **kwargs: ta.Any) -> T:
    #         return ta.cast(T, self._catalog.get_backend(self._service_cls, name, *args, **kwargs))
    #
    # def __getitem__(
    #         self,
    #         service_cls: type[T],
    # ) -> Bound[T]:
    #     return BackendCatalog.Bound(self, service_cls)
