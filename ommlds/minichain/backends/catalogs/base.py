import abc
import typing as ta

from omlish import lang


##


class BackendCatalog(lang.Abstract):
    @abc.abstractmethod
    def get_backend(self, service_cls: ta.Any, name: str, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        raise NotImplementedError

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
