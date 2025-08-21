# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from omlish.lite.cached import cached_nullary


##


class AmalgSources:
    def __init__(
            self,
            *,
            name: ta.Optional[str] = None,
            package: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._name = name or __name__
        self._package = package or __package__

    @cached_nullary
    def get_mod(self) -> ta.Any:
        import sys  # noqa
        return sys.modules[self._name]

    @cached_nullary
    def get_src(self) -> str:
        import inspect  # noqa
        return inspect.getsource(self.get_mod())

    @classmethod
    def is_src_amalg(cls, src: str) -> bool:
        for l in src.splitlines():  # noqa
            if l.startswith('# @omlish-amalg-output '):
                return True
        return False

    @cached_nullary
    def is_amalg(self) -> bool:
        return self.is_src_amalg(self.get_src())

    # TODO: read `@omlish-amalg ../scripts/manage.py`, given self._name/self._package, convert to resources path to read
    # @cached_nullary
    # def get_amalg_src(self) -> str:
    #     if _is_self_amalg():
    #         return _get_self_src()
    #
    #     import importlib.resources  # noqa
    #     return importlib.resources.files(__package__.split('.')[0] + '.scripts').joinpath('manage.py').read_text()
