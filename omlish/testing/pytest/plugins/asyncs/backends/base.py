import abc


class AsyncsBackend(abc.ABC):
    @abc.abstractmethod
    def wrap_runner(self, fn):
        raise NotImplementedError

    async def install_context(self, contextvars_ctx):
        pass
