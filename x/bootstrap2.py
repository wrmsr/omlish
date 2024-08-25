import abc
import contextlib
import dataclasses as dc
import os
import typing as ta


BootstrapConfigT = ta.TypeVar('BootstrapConfigT', bound='Bootstrap.Config')


##


class Bootstrap(abc.ABC, ta.Generic[BootstrapConfigT]):
    @dc.dataclass(frozen=True)
    class Config(abc.ABC):
        pass

    def __init__(self, config: BootstrapConfigT) -> None:
        super().__init__()
        self._config = config

    @abc.abstractmethod
    def __call__(self) -> ta.ContextManager[None]:
        raise NotImplementedError


##


class CwdBootstrap(Bootstrap['CwdBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        path: str

    @contextlib.contextmanager
    def __call__(self) -> ta.Iterator[None]:
        prev = os.getcwd()
        os.chdir(self._config.path)
        try:
            yield
        finally:
            os.chdir(prev)


##


class BootstrapHarness:
    def __init__(self, lst: ta.Sequence[Bootstrap]) -> None:
        super().__init__()
        self._lst = lst

    @contextlib.contextmanager
    def __call__(self) -> ta.Iterator[None]:
        with contextlib.ExitStack() as es:
            for c in self._lst:
                es.enter_context(c())
            yield


##


def _main() -> None:
    with BootstrapHarness([
        CwdBootstrap(CwdBootstrap.Config(
            path='..',
        )),
    ])():
        print(os.getcwd())


if __name__ == '__main__':
    _main()
