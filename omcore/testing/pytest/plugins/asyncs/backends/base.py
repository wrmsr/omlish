import abc

from ...... import lang


##


class AsyncsBackend(lang.Abstract):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def is_imported(self) -> bool:
        raise NotImplementedError

    #

    def prepare_for_metafunc(self, metafunc) -> None:  # noqa
        pass

    #

    @abc.abstractmethod
    def wrap_runner(self, fn):
        raise NotImplementedError

    async def install_context(self, contextvars_ctx):  # noqa
        pass
