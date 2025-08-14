import typing as ta

from .catalog import BackendCatalog


##


class BackendStringBackendCatalog(BackendCatalog):
    def get_backend(self, service_cls: ta.Any, name: str, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        raise NotImplementedError
