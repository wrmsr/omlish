import abc


class AsyncsBackend(abc.ABC):
    @abc.abstractmethod
    def wrap_runner(self, fn):
        raise NotImplementedError

    @abc.abstractmethod
    async def install_context(self, contextvars_ctx):
        raise NotImplementedError
